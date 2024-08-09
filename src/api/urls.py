# -*- encoding: utf-8 -*-

from starlette.endpoints import WebSocketEndpoint

from src.aop import (
    clear_cache_decorator,
    get_cache_decorator,
    only_one_exec_decorate
)
from src.oop import new_router
from src.api.views import ApiView


router = new_router()

route_list = [
    (
        "/api/position/AddPoint",
        ApiView,
        {
            "summary": "导入点位", "desc": "根据地图组给的点位文件, 并新增QC、SC等虚拟点位",
            "method_decorator": {"post": clear_cache_decorator}
        },
    ),

]

for path, cls, kw in route_list:
    if issubclass(cls, WebSocketEndpoint):
        router.add_websocket_route(path, cls)
    else:
        cls(**kw).as_view(path, router)
