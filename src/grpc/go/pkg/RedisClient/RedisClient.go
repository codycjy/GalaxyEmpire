package redisclient

import "github.com/redis/go-redis/v9"


var rdb *redis.Client

func Init() {
	rdb = redis.NewClient(&redis.Options{
		Addr:     "localhost:6379",
		Password: "", // no password set
		DB:       0,  // use default DB
})
}

func GetRedisClient() *redis.Client {
	if rdb == nil {
		Init()
	}
	return rdb
}
