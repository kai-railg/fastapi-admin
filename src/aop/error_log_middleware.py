# -*- encoding: utf-8 -*-

import time
import traceback

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.core import f_log

# https://www.starlette.io/middleware/
class ErrorLoggingMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        try:
            start_time = time.time()
            response = await call_next(request)
            process_time = round(time.time() - start_time, 2)

            if process_time > 2:
                f_log.warning(
                    f"Request {request.url.path} {request.method} took {process_time}"
                )
            response.headers["X-Process-Time"] = str(process_time) + "s"
            return response
        except Exception as e:
            f_log.error(f"Request {request.url.path} {request.method} has an error occurred: {traceback.format_exc()}")
            return JSONResponse(
                status_code=500,
                content={
                    "message": f"Internal Server Error From {self.app.title.title()}"
                }
            )
