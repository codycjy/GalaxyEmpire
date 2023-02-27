package Ginserver

import (
	redisclient "GalaxyGrpc/pkg/RedisClient"

	"github.com/gin-gonic/gin"
)

func Route() {
	r := gin.Default()
	redisclient.Init()
	defer redisclient.GetRedisClient().Close()
	r.GET("/ping", ping)

	v1:=r.Group("/api/v1")
	{
		v1.GET("/ping", pingNode)
		v1.GET("/nodes", chekcAllNodes)
		v1.POST("/node",excuteNodeCommand)
	}
	r.Run(":8089")
}


