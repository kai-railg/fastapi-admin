# -*- encoding: utf-8 -*-

import os
import time
import asyncio
import traceback
from urllib import parse
from typing import Dict, List, Tuple, Any, Iterator

import aiohttp
import aiohttp.client_exceptions
import requests
from pydantic import BaseModel, ValidationError
from requests import Response

from src.core import request_send_log as logger


class HttpResponseAdapter:
    def __init__(self, response):
        self._response: Response | aiohttp.ClientResponse = response

    @property
    def status_code(self) -> int:
        if isinstance(self._response, aiohttp.ClientResponse):
            return self._response.status
        elif isinstance(self._response, Response):
            return self._response.status_code
        raise

    def __getattr__(self, item):
        return getattr(self._response, item)


class HttpRequestHandle(object):
    def __init__(self):
        self.timeout = int(os.getenv(key="HTTP_TIMEOUT", default=4))
        self.max_retry_count = int(os.getenv("HTTP_MAX_RETRY_COUNT", 5))

    def parse_params(self, **kwargs):
        timeout = kwargs.pop("timeout", None) or self.timeout
        max_retry_count = kwargs.pop(
            "max_retry_count", None) or self.max_retry_count
        return timeout, max_retry_count

    def request_generator(self, url: str, body: Dict, **kwargs):
        timeout, max_retry_count = self.parse_params(**kwargs)
        if kwargs is not {}:
            body.update(kwargs)
        
        status, content = None, None
        for _ in range(max_retry_count):
            try:
                _resp, e = yield {
                    "url": url,
                    "timeout": timeout,
                    **body,
                    "headers": {'Content-Type': 'application/json'}
                }
                if _resp is not None:
                    resp = HttpResponseAdapter(_resp)
                    status, content = resp.status_code, resp.text and resp.json()
                    logger.info(
                        f"Response is ok. Status is {status}, url: {url}, request: {body}, response: {content}"
                    )
                    return status, content
                raise e
            
            except asyncio.TimeoutError as e:
                return 504, f"Gateway Timeout, url: {url}, request: {body}"
            except (aiohttp.client_exceptions.ClientConnectorError, requests.exceptions.ConnectionError):
                status, content = 503, f"Service Unavailable, url: {url}, request: {body}"
                time.sleep(1)
            except Exception as e:
                return 500, f"Internal Server Error, url: {url}, request: {body}, e: {traceback.format_exc()}"

        return status, content

    async def request_async(self, request, url, body, **kwargs) -> Tuple[int, Dict | str]:
        gen = self.request_generator(url, body, **kwargs)
        params = next(gen)
        while True:
            try:
                result, e = None, None
                try:
                    async with aiohttp.ClientSession(raise_for_status=True) as session:
                        async with session.request(request, url, **params) as response:
                            return await response.read()

                except Exception as _e:
                    e = _e
                params = gen.send((result, e))
            except StopIteration as e:
                return e.value

    def request_sync(self, request, url, body, **kwargs) -> Tuple[int, Dict | str]:
        gen = self.request_generator(url, body, **kwargs)
        params = next(gen)
        while True:
            try:
                result, e = None, None
                try:
                    result = request(**params)
                except Exception as _e:
                    e = _e
                params = gen.send((result, e))
            except StopIteration as e:
                return e.value


class RequestSendProxy(object):
    service_name_mapping: Dict[str, 'RequestSendProxy'] = {}
    http_handle = HttpRequestHandle()

    def __init__(self):
        self.SERVICE_HOST = os.environ.get('SERVICE_HOST', case=str, default='127.0.0.1')
        self.SERVICE_PORT: int = os.environ.get('SERVICE_HOST', case=int, default=8000)
        self.SERVICE_NAME: str = os.environ.get('SERVICE_NAME', case=str, default="Default Service Name")
        self.protocol: str = "http"

    # todo
    def get_all_urls_from_service_name(self) -> Iterator:
        """
        获取 service 对应的所有 url, 返回迭代器
        :param service_name:
        :return:
        """
        yield f"{self.protocol}://{self.SERVICE_HOST}:{self.SERVICE_PORT}"

    def check_status_code(self, status_code: int) -> bool:
        if 400 <= status_code < 600:
            return False
        return True

    def request_generator(self, request, api, body: Dict, **kwargs):

        notification_policy = kwargs.pop(
            "notification_policy", None) or "single"
        resp_model: BaseModel = kwargs.pop("resp_model", None)
        urls = self.get_all_urls_from_service_name()

        status, resp = None, None
        for url in urls:
            url = parse.urljoin(url, api)
            status, resp = yield dict(
                request=request,
                url=url,
                body=body,
                **kwargs
            )
            # 遇到请求失败的实例, 重试其他实例
            if self.check_status_code(status) is False:
                logger.error(
                    f"The status code is {status}, resp is {resp}, url is {url}, body is {body}, resp is {resp}")
                continue

            try:
                resp = resp_model.model_validate(resp) if resp_model else resp
            except ValidationError as e:
                logger.error(e)

            # 一旦有任一实例请求成功, 则退出
            if notification_policy == "single":
                return status, resp
        if status is None:
            return 502, "Bad Gateway, failed to get all instances"
        return status, resp

    def request_sync(self, request, api, body: Dict, **kwargs) -> Tuple:
        """
        异步http 请求, 调用 aio_http 中的方法
        :param request:
        :param api:
        :param body:
        :kw:
            - notification_policy: single, all, appoint;
            - service_name
        :return:
        """

        gen = self.request_generator(request, api, body, **kwargs)
        params = next(gen)
        while True:
            try:
                result = self.http_handle.request_sync(
                    **params
                )
                params = gen.send(result)
            except StopIteration as e:
                return e.value

    async def request(self, method, api, body: Dict, **kwargs) -> Tuple:
        """
        异步http 请求, 调用 aio_http 中的方法
        :param request:
        :param api:
        :param body:
        :kw:
            - notification_policy: single, all, appoint;
            - service_name
        :return:
        """
        gen = self.request_generator(method, api, body, **kwargs)
        params = next(gen)
        while True:
            try:
                result = await self.http_handle.request_async(
                    **params
                )
                params = gen.send(result)
            except StopIteration as e:
                return e.value
