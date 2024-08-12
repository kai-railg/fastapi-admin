# -*- coding: utf-8 -*-

import uuid
import asyncio
from http import client

from redis import asyncio as aioredis

from src.db import redis_db


class AsyncRedisLock:
    def __init__(
            self,
            redis_client: aioredis.client.Redis=None,
            key: str="",
            lock_timeout: int = 60 * 1000, # ms
            token: str = None,
            retry_interval: float = 0.1
    ):
        """

        :param redis_client:  asyncio redis client
        :param key: usually the service name
        :param lock_timeout: default 60s
        :param token:
        :param retry_interval:
        """
        self.redis_client = redis_client  or redis_db
        self.key = key
        self.lock_timeout = lock_timeout
        self.token = token or str(uuid.uuid4())
        self.retry_interval = retry_interval
        
        if not self.redis_client:
            raise ValueError(f"The redis client is {self.redis_client}")
        if not self.key:
            raise ValueError(f"The key is {self.key}")

    def lock(self, key: str, **kwargs) -> aioredis.client.Lock:
        """
        redis 提供的 Lock 对象，功能更丰富
        :param key:
        :param kwargs:
        :return:
        """
        return self.redis_client.lock(name=key, **kwargs)

    async def _acquire(self):
        """尝试获取锁"""
        while True:
            if await self.redis_client.set(self.key, self.token, nx=True, px=self.lock_timeout):
                return True
            # 等待一段时间后重试
            await asyncio.sleep(self.retry_interval)

    async def _release(self):
        """释放锁"""
        # 使用Lua脚本确保操作的原子性
        script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        return await self.redis_client.eval(script, 1, self.key, self.token)

    async def __aenter__(self):
        await self._acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._release()


# 使用示例
if __name__ == "__main__":
    # client = aioredis.Redis(host='localhost', port=6379, db=0)
    lock = AsyncRedisLock("", 'my_lock', 50000, token="123456")  # 锁定时间为5000毫秒


    async def run():
        print("run ...")
        async with lock:
            print(lock, type(lock))
            print("Lock acquired. Doing work.")
            # 在这里执行你需要同步的代码
            await asyncio.sleep(10)

        await client.aclose()


    asyncio.run(run())
