package main

import (
	"fmt"
	"net/http"
	"strings"
	"sync"

	"github.com/gin-gonic/gin"
	"gorm.io/driver/mysql"
	"gorm.io/gorm"
)

type Planet struct {
	ID        uint   `gorm:"primary_key" json:"id"`
	Server    string `gorm:"-" json:"server"`  // gorm ignore
	Name      string `json:"name"`
	Position  string `gorm:"column:pos" json:"pos"`
	Crystal   int    `json:"crystal"`
	Metal     int    `json:"metal"`
	HasAlly   int    `json:"has_ally"`
	AllyName  string `json:"ally_name"`
}

var db *gorm.DB
var once sync.Once

func connectDB() *gorm.DB {
	once.Do(func() {
		dsn := "galaxy:@tcp(localhost:3306)/galaxyscan?charset=utf8mb4&parseTime=True&loc=Local"

		var err error
		db, err = gorm.Open(mysql.Open(dsn), &gorm.Config{})
		if err != nil {
			panic("failed to connect database")
		}
	})
	return db
}

func queryUsername(c *gin.Context){
	planet := Planet{}
	err:=c.BindJSON(&planet)
	if err != nil {
		c.JSON(400, gin.H{
			"message": "Bad request",
		})
		return
	}
	db:=connectDB()
	result:=[]Planet{}
	db.Table(planet.Server).Where("name like ?", planet.Name+"%").Find(&result)
	c.JSON(200, result)
}

func queryAlly(c *gin.Context){
	planet := Planet{}
	err:=c.BindJSON(&planet)
	if err != nil {
		c.JSON(400, gin.H{
			"message": "Bad request",
		})
		return
	}
	db:=connectDB()
	result:=[]Planet{}
	db.Table(planet.Server).Where("ally_name like ?", planet.AllyName+"%").Find(&result)
	c.JSON(200, result)
}

func queryPostion(c *gin.Context){
	planet := Planet{}
	err:=c.BindJSON(&planet)
	if err != nil {
		c.JSON(400, gin.H{
			"message": "Bad request",
		})
		return
	}
	db:=connectDB()
	result:=[]Planet{}
	db.Table(planet.Server).Where("pos= ?", planet.Position).Find(&result)
	c.JSON(200, result)
}

func queryAmbiguousPosition(c *gin.Context){
	planet := Planet{}
	err:=c.BindJSON(&planet)
	if err != nil {
		c.JSON(400, gin.H{
			"message": "Bad request",
		})
		return
	}
	db:=connectDB()
	result:=[]Planet{}
	db.Table(planet.Server).Where("pos LIKE ?", planet.Position+"%").Find(&result)
	c.JSON(200, result)
}
func queryServer(c *gin.Context) {
	db := connectDB()
	var tables []string
	err := db.Raw("SHOW TABLES").Scan(&tables).Error
	if err != nil {
		c.JSON(http.StatusBadGateway, gin.H{
			"message": "Server error",
		})
		return
	}

	filteredTables := make([]string, 0)
	excludeString := "server" // 替换为你想要剔除的特定字符

	for _, table := range tables {
		if !strings.Contains(table, excludeString) {
			filteredTables = append(filteredTables, table)
		}
	}

	c.JSON(http.StatusOK, filteredTables)
}


type ServerStatus struct {
	ID uint `gorm:"primary_key" json:"id"`
	ServerName string `json:"server"`
	LastUpdated string `json:"last_modified"`
}

func queryServerStatus(c *gin.Context) {
	db := connectDB()
	server := c.Params.ByName("server")

	fmt.Println(server)
	var serverStatus ServerStatus
	if err := db.Table("servers_status").Where("server_name = ?", server).First(&serverStatus).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Server not found"})
		return
	}
	c.JSON(200, serverStatus)
}

func main(){
	r:=gin.Default()

	r.GET("/ping", func(c *gin.Context){
		c.JSON(200, gin.H{
			"message": "pong",
		})
	})

	scan:=r.Group("/api/scan")
	{
		scan.POST("/user", queryUsername)
		scan.POST("/ally", queryAlly)
		scan.POST("/pos", queryPostion)
		scan.POST("/pos/ambiguous", queryAmbiguousPosition)
		scan.GET("/server", queryServer)
		scan.GET("/status/:server", queryServerStatus)
	}
	r.Run()

}
