# -*- encoding: utf-8 -*-

import asyncio
import functools
import collections
from typing import List, Dict, Any

from pydantic import BaseModel

from src.core import f_log


class LocalEvent(asyncio.Event):
    """
    对应asyncio.Event, 相比于 Condition, event 避免了多次加锁。
    新增 set_val 和 wait_val 方法, 使其可以直接获取到结果
    """

    def __init__(self) -> None:
        super().__init__()
        self._save_val = None

    def set_val(self, val) -> None:
        """Set the internal flag to true. All coroutines waiting for it to
        become true are awakened. Coroutine that call wait() once the flag is
        true will not block at all.
        """
        if not self._value:
            self._value = True
            self._save_val = val

            for fut in self._waiters:
                if not fut.done():
                    fut.set_result(val)

    async def wait_val(self):
        # 为了防止丢失 set_val 方法
        if self._save_val:
            return self._save_val

        if self._value:
            raise Exception("event status is true, but no val")

        fut = self._get_loop().create_future()
        self._waiters.append(fut)
        try:
            result = await fut
            return result
        finally:
            self._waiters.remove(fut)


class Cache(object):
    def __init__(self):
        self.cache_map = {}

    def get(self, key) -> Any:
        return self.cache_map.get(key)

    def set(self, key, value) -> None:
        self.cache_map[key] = value

    def clear(self) -> None:
        self.cache_map.clear()

    def get_key(self, request_body: BaseModel | str, func, cls_name: str) -> str:
        if isinstance(request_body, BaseModel):
            cache_key = request_body.model_dump_json()
        else:
            cache_key = str(request_body)
        return cls_name + ":" + func.__name__ + ":" + cache_key


cache = Cache()
e_list: Dict[str, List[LocalEvent]] = collections.defaultdict(list)


# 清除缓存的装饰器, 用于更新箱子的函数
def clear_cache_decorator(func):
    @functools.wraps(func)
    async def wrap(cls_name, *args, **kwargs):

        f_log.info(f"clear_cache_decorator clear cache...")
        result = await func(*args, **kwargs)
        cache.clear()

        return result

    return wrap


# 请求箱子信息的装饰器, 仅用于查询接口
def get_cache_decorator(func):
    @functools.wraps(func)
    async def wrap(cls_name, *args, **kwargs):
        cache_key = cache.get_key(kwargs.get("request_body"), func, cls_name)
        result = cache.get(cache_key)
        if result:
            return result

        # 可以模拟并发请求
        # await asyncio.sleep(5)

        e_list_length = len(e_list[cache_key])

        event = LocalEvent()

        # append 操作是原子性的
        e_list[cache_key].append(event)

        # 1. 单线程才可以这样写
        # 2. 这里不要加await的操作, 否则 len(e_list[cache_key]) 可能 != 1

        if e_list_length == 0 and len(e_list[cache_key]) == 1:
            # 为了避免缓存击穿, 只对第一个请求调用请求函数, 其他的请求则通过 event.wait_val 获取结果
            async def get_result():
                # 当上一批的 event 全部已经 set_val, 就可以不用调用请求函数
                result = cache.get(cache_key)
                if not result:
                    result = await func(*args, **kwargs)
                    cache.set(cache_key, result)
                # 这里缓存被清理也没事
                while e_list[cache_key]:
                    e_list[cache_key].pop().set_val(result)

            _task = asyncio.create_task(get_result())

        # 这里不要加await的操作, 否则可能丢失 set_val 方法
        # # await asyncio.sleep(5)
        return await event.wait_val()

    return wrap

# 防止重复执行的装饰器, 用于回调接口, 相同事件的请求, 只执行一次


def only_one_exec_decorate(func):
    @functools.wraps(func)
    async def wrap(cls_name, *args, **kwargs):
        cache_key = cache.get_key(kwargs.get("request_body"), func, cls_name)

        e_list_length = len(e_list[cache_key])

        event = LocalEvent()

        e_list[cache_key].append(event)

        # 1. 单线程才可以这样写
        # 2. 这里不要加await的操作, 否则 len(e_list[cache_key]) 可能 != 1

        if e_list_length == 0 and len(e_list[cache_key]) == 1:
            async def get_result():
                result = await func(*args, **kwargs)
                while e_list[cache_key]:
                    e_list[cache_key].pop().set_val(result)

            _task = asyncio.create_task(get_result())

        # 这里不要加await的操作, 否则可能丢失 set_val 方法
        # # await asyncio.sleep(5)
        return await event.wait_val()
    return wrap
