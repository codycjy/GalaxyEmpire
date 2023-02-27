from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AllNodeStatus(_message.Message):
    __slots__ = ["node"]
    NODE_FIELD_NUMBER: _ClassVar[int]
    node: _containers.RepeatedCompositeFieldContainer[NodeStatus]
    def __init__(self, node: _Optional[_Iterable[_Union[NodeStatus, _Mapping]]] = ...) -> None: ...

class Empty(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class Node(_message.Message):
    __slots__ = ["server", "username"]
    SERVER_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    server: str
    username: str
    def __init__(self, server: _Optional[str] = ..., username: _Optional[str] = ...) -> None: ...

class NodePing(_message.Message):
    __slots__ = ["message", "server", "username"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    SERVER_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    message: str
    server: str
    username: str
    def __init__(self, message: _Optional[str] = ..., server: _Optional[str] = ..., username: _Optional[str] = ...) -> None: ...

class NodePong(_message.Message):
    __slots__ = ["message"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...

class NodeStatus(_message.Message):
    __slots__ = ["node", "status"]
    NODE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    node: Node
    status: str
    def __init__(self, node: _Optional[_Union[Node, _Mapping]] = ..., status: _Optional[str] = ...) -> None: ...

class ReqNodeCommand(_message.Message):
    __slots__ = ["command", "node"]
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    NODE_FIELD_NUMBER: _ClassVar[int]
    command: str
    node: Node
    def __init__(self, node: _Optional[_Union[Node, _Mapping]] = ..., command: _Optional[str] = ...) -> None: ...

class ResNodeCommand(_message.Message):
    __slots__ = ["message"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...
