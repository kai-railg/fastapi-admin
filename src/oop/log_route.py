# -*- encoding: utf-8 -*-

import json
import traceback
from typing import Callable
from fastapi import APIRouter, Request, Response
from fastapi.routing import APIRoute

from src.core import request_get_log, request_post_log

def try_format(body):
    try:
        rs = json.loads(body)
        rs = json.dumps(rs, indent=4, ensure_ascii=False)
    except Exception as exc:
        rs = body
    return rs


class LogReqContextRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            req_id = id(request)
            req_info = {
                "id": req_id,
                "method": request.method,
                # "headers": request.headers.items(),
                "param": request.query_params.items(),
                "client": request.client,
            }
            if request.method == "GET":
                logger_req = request_get_log
            else:
                logger_req = request_post_log
            try:
                response = await original_route_handler(request)
            except Exception as exc:
                logger_req.error(f"error new request \"{request.url.path}\": {req_info}: {traceback.format_exc()}")
                body = await request.body()
                req_body = try_format(body)
                logger_req.error(f"detail [{req_id}]\n<<<<<<<<<<<< \n{req_body}\n============")
                raise exc
            body = await request.body()
            req_body = try_format(body)
            res_body = try_format(response.body)
            logger_req.info(f"new request \"{request.url.path}\": {req_info}")
            logger_req.info(f"detail [{req_id}]\n<<<<<<<<<<<< \n{req_body}\n>>>>>>>>>>>>\n{res_body}\n============")
            return response
        return custom_route_handler


def new_router():
    return APIRouter(route_class=LogReqContextRoute)
