package GrpcClient

import (
	pb "GalaxyGrpc/pkg/pb"
	"context"
	"fmt"
	"log"

	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

func rescue(){
	if r := recover(); r != nil {
		println("Recovered in f", r)
	}
}
func PingNode(url string,server string,username string)bool {
	conn, err := grpc.Dial(url, grpc.WithTransportCredentials(insecure.NewCredentials()))
	defer rescue()
	if(err != nil){
		fmt.Println("panic")
		panic(err)
	}
	defer conn.Close()
	client:=pb.NewGalaxyGrpcClient(conn)
	_, err = client.PingNode(context.Background(), 
		&pb.NodePing{Server: server,Username: username})
	return err==nil 
}


func GetAllNodeInfo(url string)[]*pb.NodeStatus{
	conn, err := grpc.Dial(url, grpc.WithTransportCredentials(insecure.NewCredentials()))
	defer rescue()
	if(err != nil) {
		log.Fatal(err)
	}
	defer conn.Close()
	client:=pb.NewGalaxyGrpcClient(conn)
	res, err := client.GetAllNodeStatus(context.Background(), 
	&pb.Empty{})
	fmt.Println(err)
	if(err != nil) {
		return nil
	}
	return res.GetNode()
}

func ExcuteNodeCommand(url string,server string,username string,command string )string {
	conn, err := grpc.Dial(url, grpc.WithTransportCredentials(insecure.NewCredentials()))
	defer rescue()
	if(err != nil) {
		log.Fatal(err)
	}
	defer conn.Close()
	client:=pb.NewGalaxyGrpcClient(conn)
	res, err := client.ExcuteNodeCommand(context.Background(), 
	&pb.ReqNodeCommand{
			Node: &pb.Node{
				Server:server,
				Username: username,
			},
			Command: command,
	})
	if(err != nil) {
		return ""
	}
	return res.GetMessage()
}


