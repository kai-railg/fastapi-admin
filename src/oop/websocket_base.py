# -*- coding: utf-8 -*-

import typing

from starlette.websockets import WebSocket
from starlette.endpoints import WebSocketEndpoint
from src.core.log import websocket_log
from src.oop import BroadCaster

class BaseWebSocketEndpoint(WebSocketEndpoint):
    # 类变量, 需要在子类中定义
    _clients = None
    _boradcaster = None

    @property
    def clients(self) -> typing.List[WebSocket]:
        return self._clients
    
    @classmethod
    def get_clients(cls)-> typing.List[WebSocket]:
        return cls._clients

    @classmethod
    def set_clients(cls):
        cls._clients = []

    @classmethod
    def set_boradcaster(cls, bc: BroadCaster):
        if cls.get_boradcaster():
            raise Exception(f"{cls.__name__} broadcaster already set")
        cls._boradcaster = bc

    @classmethod
    def get_boradcaster(cls)-> BroadCaster:
        return cls._boradcaster

    @classmethod
    async def put_data(cls, data):
        await cls.get_boradcaster().put(data)

    @classmethod
    async def get_data(cls):
        while True:
            data = await cls.get_boradcaster().get()
            if data:
                await cls.board_cast(data)

    @classmethod
    async def board_cast(cls, message: typing.Any) -> None:
        for client in cls.get_clients():
            try:
                await client.send_json(message)
            except Exception as e:
                websocket_log.error(f"websocket send message error: {e}")

    async def on_connect(self, websocket: WebSocket) -> None:
        """Override to handle an incoming websocket connection"""
        await websocket.accept()
        client = self.scope["client"]
        ip, port = client[0], client[1]

        websocket_log.info(
            f"{id(websocket)} websocket connect, {ip, port}, current clients: {len(self.clients) + 1}"
        )
        if websocket not in self.clients:
            self.clients.append(websocket)

    async def on_receive(self, websocket: WebSocket, data: typing.Any) -> None:
        """Override to handle an incoming websocket message"""
        await websocket.send_json({"received": data, "message": "ok"})

    async def on_disconnect(self, websocket: WebSocket, close_code: int) -> None:
        """Override to handle a disconnecting websocket"""

        if websocket in self.clients:
            self.clients.remove(websocket)

        websocket_log.info(
            f"{id(websocket)} websocket disconnect, current clients: {len(self.clients)}"
        )
