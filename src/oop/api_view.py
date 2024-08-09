# -*- coding: utf-8 -*-

import inspect
import functools
from typing import List

from fastapi import APIRouter


class BaseApiView(object):

    def __init__(self, **kwargs):
        self.method_keys = [
            "post",
            "get",
            "put",
            "delete",
            "patch",
            "head",
            "options",
            "websocket",
        ]
        self._description = kwargs.get("desc") or "Api Description"
        self._summary = kwargs.get("summary") or "Api Summary"
        self._tags = kwargs.get("tags") or []
        self.method_decorator: dict = kwargs.get("method_decorator", {})

    def func_decorator(self, func):

        async def dispatch(*args, **kwargs):

            # 列表装饰器, 按照索引顺序执行
            method_dec = self.method_decorator.get(func.__name__)
            if not method_dec:
                return await func(*args, **kwargs)
            
            if not isinstance(method_dec, list):
                method_dec = [method_dec]
            decorated_function = func
            for md in method_dec:
                decorated_function = md(decorated_function)
            return await decorated_function(self.__class__.__name__, *args, **kwargs)


        @functools.wraps(func)
        async def wrap(*args, **kwargs):
            return await dispatch(*args, **kwargs)

        def dispatch_sync(*args, **kwargs):
            # 列表装饰器, 按照索引顺序执行
            method_dec = self.method_decorator.get(func.__name__)
            if not method_dec:
                return func(*args, **kwargs)
            
            if not isinstance(method_dec, list):
                method_dec = [method_dec]
            decorated_function = func
            for md in method_dec:
                decorated_function = md(decorated_function)
            return decorated_function(self.__class__.__name__, *args, **kwargs)


        @functools.wraps(func)
        async def wrap_sync(*args, **kwargs):
            return dispatch_sync(*args, **kwargs)

        is_async = inspect.iscoroutinefunction(func)
        return wrap if is_async else wrap_sync

    def as_view(self, path: str, route: APIRouter, **kwargs) -> None:
        """ """
        for method in self.method_keys:
            if hasattr(self, method):
                func = getattr(self, method)
                route.add_api_route(
                    path,
                    self.func_decorator(func),
                    methods=[method.upper()],
                    description=self.description,
                    summary=self.summary,
                    tags=self.tags,
                    **kwargs,
                )

    @property
    def tags(self) -> List:
        return self._tags

    @property
    def description(self) -> str:
        return self._description

    @property
    def summary(self) -> str:
        return self._summary

    @description.setter
    def description(self, desc: str) -> None:
        self._description = desc

    @summary.setter
    def summary(self, summary: str) -> None:
        self._summary = summary

