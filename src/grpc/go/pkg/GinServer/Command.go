package Ginserver

type NodeCommand struct{
	Node Node `json:"node"`
	Command string `json:"command"`
}
