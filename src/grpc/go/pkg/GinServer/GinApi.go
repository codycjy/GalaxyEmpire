package Ginserver

import (
	client "GalaxyGrpc/pkg/GrpcClient"
	redisclient "GalaxyGrpc/pkg/RedisClient"
	pb "GalaxyGrpc/pkg/pb"
	"context"

	"github.com/gin-gonic/gin"
)

func ping(c *gin.Context) {
	c.JSON(200, gin.H{
		"message": "pong",
	})
}

func pingNode(c *gin.Context) {
	node:=Node{}
	c.ShouldBindJSON(&node)

	rdb:=redisclient.GetRedisClient()
	grpcAddress:=rdb.Get(context.Background(),node.NodeServer+"@"+node.NodeUsername).Val()

	if grpcAddress==""{
		c.JSON(200, gin.H{
			"message": "node not found",
		})
		return
	}

	res:=client.PingNode(grpcAddress,node.NodeServer,node.NodeUsername)
	c.JSON(200, gin.H{"survived":res, })
}

func chekcAllNodes(c *gin.Context) {
	rdb:=redisclient.GetRedisClient()
	serverList:=rdb.Do(context.Background(),"get","server").Val().([]string)
	if len(serverList)==0{
		c.JSON(200, gin.H{
			"message": "no server found",
		})
		return
	}
	res:=[]*pb.NodeStatus{}
	for _,server:=range serverList{
		statusList:=client.GetAllNodeInfo(server)
		res=append(res,statusList...)
	}
	// res:=client.GetAllNodeInfo("localhost:50051")
	c.JSON(200, gin.H{"survived":res, })
}


func excuteNodeCommand(c *gin.Context){
	nodeCommand:=NodeCommand{}
	c.ShouldBindJSON(&nodeCommand)
	node:=nodeCommand.Node
	rdb:=redisclient.GetRedisClient()
	grpcAddress:=rdb.Get(context.Background(),node.NodeServer+"@"+node.NodeUsername).Val()

	if grpcAddress==""{
		c.JSON(200, gin.H{
			"message": "node not found",
		})
		return
	}
	res:=client.ExcuteNodeCommand(grpcAddress,
		nodeCommand.Node.NodeServer,
		nodeCommand.Node.NodeUsername,
		nodeCommand.Command)
	c.JSON(200,gin.H{
		"msg":res,
	})

}
