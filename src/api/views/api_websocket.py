# -*- encoding: utf-8 -*-

import typing

from starlette.websockets import WebSocket
from src.oop import BaseWebSocketEndpoint

class ApiWebsocket(BaseWebSocketEndpoint):
    
    async def on_receive(self, websocket: WebSocket, data: typing.Any) -> None:
        """Override to handle an incoming websocket message"""
        await super().on_receive(websocket, data)
        await self.put_data({"message": "test broad data", "ok": "ok"})