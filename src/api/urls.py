# -*- encoding: utf-8 -*-


import asyncio
from src.aop import (
    clear_cache_decorator,
    get_cache_decorator,
    only_one_exec_decorate
)
from src.oop import new_router, BaseWebSocketEndpoint, BroadCasterCls
from src.api.views import *
from src.schema import StdRes


router = new_router()

route_list = [
    (
        "/api/test",
        ApiView,
        {
            "summary": "api summary", "desc": "api desc",
            "method_decorator": {"post": clear_cache_decorator}
        },
    ),
    (
        "/ws/test",
        ApiWebsocket,
        {
            "summary": "websocket api summary", "desc": "websocket api desc",
        },
    ),

]

for path, cls, kw in route_list:
    if issubclass(cls, BaseWebSocketEndpoint):
        router.add_websocket_route(path, cls)
        cls.set_clients()
        cls.set_boradcaster(BroadCasterCls(topic=path))
        asyncio.create_task(cls.get_data())
    else:
        cls(**kw).as_view(path, router)
