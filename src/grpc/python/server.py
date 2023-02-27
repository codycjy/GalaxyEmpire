import sys
from time import sleep
import grpc
from concurrent import futures
import redis

from .pb import service_pb2
from .pb import service_pb2_grpc
from .pb.service_pb2 import NodeStatus,AllNodeStatus,ReqNodeCommand,ResNodeCommand,Node
from ...GalaxyNode.GalaxyController import GalaxyController 


class GalaxyGrpcServer(service_pb2_grpc.GalaxyGrpc,GalaxyController):
    def __init__(self,server="localhost",port=50051) -> None:
        super(GalaxyGrpcServer, self).__init__()
        self.server=server
        self.port=port
        self.Rconn=redis.Redis(host="localhost",port=6379,db=0)
        self.Rconn.lpush("server","%s:%s"%(self.server,self.port))

    def __del__(self) -> None:
        for i in self.nodes:
            for j in self.nodes[i]:
                if self.nodes[i][j].is_alive():
                    print("terminating",i,j)
                    self.nodes[i][j].terminate()
                self.Rconn.delete(f"{i}@{j}")
        self.Rconn.close()

    
    def addNode(self, info, needLoginTest=True):
        result=super().addNode(info, needLoginTest)
        if result['status']:
            self.Rconn.set(f"{info['meta']['server']}@{info['meta']['username']}",
                           f"{self.server}:{self.port}")
        return result
    def pingNode(self, request, context):

        if self.checkNodeExist(request.server,request.username):
            msg=self.nodes[request.server][request.username].ping()
            return service_pb2.NodePong(message=msg)
        else:
            return service_pb2.NodePong(message="Node not found")

    def getAllNodeStatus(self, request, context):
        nodeList=[]
        for node in self.nodesInfo:
            nodeList.append(NodeStatus(node=Node(
                                           server=node[0],
                                           username=node[1]
                                       ),
                                       status=self.nodesInfo[node]['status']))
        return AllNodeStatus(node=nodeList)

    def ExcuteNodeCommand(self,request:ReqNodeCommand,context) -> ResNodeCommand:
        msg=request.command
        node=request.node
        if self.checkNodeExist(node.server,node.username):
            if msg in ("start","end"):
                try:
                    if msg=="start":
                        self.nodes[node.server][node.username].start()
                    else:
                        self.nodes[node.server][node.username].terminate()
                    return ResNodeCommand(message="succeed")
                except Exception as e:
                    return ResNodeCommand(message=f"failed {e}")
            else:
                result=self.commandNode(node.server,node.username,msg)
                return ResNodeCommand(message=result)
        else:
            return ResNodeCommand(message="Node doesn't exists")
        

    def serve(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        service_pb2_grpc.add_GalaxyGrpcServicer_to_server(self, server)
        server.add_insecure_port('[::]:%s' % self.port)
        server.start()
        try:
            print("server started")
            server.wait_for_termination()
        except KeyboardInterrupt:
            sys.exit()


