import configparser
import os
from collections import defaultdict
from multiprocessing import Pipe
import logging
import time

from src.Core.GalaxyCore import GalaxyCore
from src.GalaxyNode.GalaxyNode import GalaxyNode
from src.Logger.Logger import GalaxyLogger


class GalaxyController:
    def __init__(self, **kwargs):
        self.nodes = defaultdict(dict)
        self.nodesInfo = defaultdict(dict)
        self.conns = defaultdict(dict)
        self.cfgBackup = defaultdict(dict)
        self.defaultFleet = GalaxyCore.fleet
        self.loggingPath:str= kwargs.get("loggingPath", './logs')
        self.loggingLevel:int = kwargs.get("loggingLevel", logging.INFO)
        self.controllerLogger = GalaxyLogger(self.loggingPath,
                                             self.loggingLevel,
                                             kwargs.get(
                                                 "controllerName", "GalaxyController")
                                             )

    def addNode(self, info, needLoginTest=True):
        conn1, conn2 = Pipe()
        logger = GalaxyLogger(info['loggingPath'], info['loggingLevel'],
                              f"{info['meta']['username']}@{info['meta']['server']}")

        node = GalaxyNode(conn2)
        node.getTaskNew(info)

        node.setLogger(logger)
        node.fleet = self.defaultFleet
        server = info['meta']['server']
        username = info['meta']['username']

        self.cfgBackup[server][username] = info

        if needLoginTest:
            testLoginResult = node.testLogin()
            if testLoginResult['status']:
                self.nodes[server][username] = node
                self.conns[server][username] = conn1
                return {'status': True, 'msg': 'Node added'}
            else:
                print(
                    f"Node {username} on {server} login failed: {testLoginResult['msg']}")
                return {'status': False, 'msg': testLoginResult['msg']}
        else:
            self.nodes[server][username] = node
            self.conns[server][username] = conn1

        print(f"Node {username} on {server} added")
        self.nodesInfo[(server, username)] = {"status": "idle"}
        return {'status': True, 'msg': 'Node added'}

    @staticmethod
    def checkNodeStatus(node):
        if node.pid is None:
            return "idle"
        else:
            if node.is_alive():
                return "running"
            else:
                return "dead"

    def checkAllNodeStatus(self):
        for i in self.nodes:
            for j in self.nodes[i]:
                self.nodesInfo[(i, j)]["status"] = self.checkNodeStatus(
                    self.nodes[i][j])


    def getAllNodesInfo(self) -> list:
        return list(self.nodesInfo.items())

    def checkAlive(self):  # Alpha version
        for server in self.nodes.values():
            for nodes in server.keys():
                if not nodes.is_alive():
                    try:
                        print(f"Node {nodes} on {server} is dead, restarting")
                        self.addNode(self.cfgBackup[server][nodes], False)
                        self.nodes[server][nodes].start()
                        print(f"Node {nodes} on {server} restarted")
                    except Exception as e:
                        print(e)

    def loadConfigs(self, path: str = 'NodeConfigs'):
        configs = []
        curPath = os.getcwd()  # TODO: check directory
        if not os.path.exists(curPath + '/' + path):
            print('Error! Config directory not found')
            os.mkdir(curPath + '/' + path)
            return []
        cfgPath = curPath + f'/{path}'
        configPath = [i for i in os.listdir(cfgPath) if i.endswith('.ini')]
        if not configPath:
            print("Warning! No config file found")
        config = configparser.ConfigParser()
        for i in configPath:
            if i.endswith('.ini'):
                try:
                    config.read(cfgPath + f'/{i}')
                    configs.append(self.parseConfig(config))
                except Exception as e:
                    print(e)
        return configs

    def findNode(self, username: str, server: str):
        return self.nodes.get(server, {}).get(username, None)

    def start(self):
        for i in self.nodes:
            for j in self.nodes[i]:
                print(f"Starting node {j} on {i}")
                self.nodes[i][j].start()
        print("All nodes started")

    def stop(self):
        for i in self.nodes:
            for j in self.nodes[i]:
                self.nodes[i][j].terminate()

    def sendMsg(self, server:str, username:str,msg:str):
        if self.checkNodeExist(server, username):
            self.conns[server][username].send(msg)
        else:
            self.controllerLogger.warning(
                f"Node {username} on {server} not found")

    def recvMsg(self,  server:str,username:str,timeout=5):  # TODO: Change it later
        """
        Receive message from node
        :param server: server name
        :param username: username
        :param timeout: timeout
        :return: message
        """
        if not self.checkNodeExist(server,username):
            return "Node doesn't exists"
        now=time.time()

        while time.time()-now<timeout:
            if self.conns[server][username].poll():
                response=self.conns[server][username].recv()
                return str(response)
            time.sleep(0.1)
        self.controllerLogger.info(
            f"Node {username} on {server} has no message")
        return "Node has no message"

    def commandNode(self,server:str,username:str,command:str):
        if not self.checkNodeExist(server,username):
            return "Node doesn't exists!"
        self.sendMsg(server,username,command)
        message=self.recvMsg(server,username)
        print("message: ",message)
        return str(message)
            

    def autoGetNode(self, path="NodeConfigs", needLoginTest=True):
        nodeList = self.loadConfigs(path)
        if nodeList:
            for i in self.loadConfigs(path):
                i['loggingPath'] = self.loggingPath
                i['loggingLevel'] = self.loggingLevel
                self.addNode(i, needLoginTest=needLoginTest)

    def checkNodeExist(self, server, username):
        return username in self.nodes[server].keys()

    def parseConfig(self, config):  # TODO rewrite task with dict
        nodeConfig = defaultdict(dict)
        isError = False
        if config.has_section('Task') and config.has_section('Base'):
            tasks = config.items('Task')
            infoRaw = config.items('Base')
            infoDict = {}
            for i in infoRaw:
                infoDict[i[0]] = i[1]
            if not infoDict.get('username', None) \
                    or not infoDict.get('password', None) \
                    or not infoDict.get('server', None):
                isError = True
                print("Error: Base info is not complete")
            else:
                nodeConfig['meta'] = infoDict

            for i in tasks:
                try:
                    if i[0] == 'attack' and int(i[1]) == 1:
                        nodeConfig['enabled']['attack'] = True
                        attackConfig = self.parseTask(config.items('Attack'))
                        if attackConfig:
                            nodeConfig['attack'] = attackConfig
                        else:
                            print("Error in attack config")
                            isError = True
                    if i[0] == 'explore' and int(i[1]) == 1:
                        nodeConfig['enabled']['explore'] = True
                        exploreConfig = self.parseTask(config.items('Explore'))
                        if exploreConfig:
                            nodeConfig['explore'] = exploreConfig
                        else:
                            print("Error in explore config")
                            isError = True
                    if i[0] == 'escape' and int(i[1]) == 1:
                        nodeConfig['enabled']['escape'] = True
                except ValueError:
                    print("Error in config file")
                    return None
        else:
            print('Error! Config file is not valid, Required sections: Task, Base')
        if isError:
            return None
        return nodeConfig

    def parseTask(self, rawTask):
        data = {}
        task = {}
        isError = False
        for i in rawTask:
            data[i[0]] = i[1]
        try:
            target = data['target'].split(',')
            task['target'] = [list(map(int, i.split('.'))) for i in target]
        except ValueError:
            isError = True
            # TODO: low priority add to loggers
        except Exception as e:
            print(e)

        try:
            times = int(data['times'])
            task['times'] = times
            startFrom = int(data['start_from'])
            task['startFrom'] = startFrom
            level = int(data['fleet'])
            task['level'] = level
        except ValueError:
            isError = True


        if isError:
            self.controllerLogger.error("Error in target")
            return {}
        return task

    def autoLoadTask(self, path):
        for i in self.loadConfigs(path):
            self.addNode(i)


if __name__ == '__main__':
    pass
