# -*- coding: utf-8 -*-

import os
import json
import asyncio
import traceback
from typing import Callable, Any

from redis import asyncio as aioredis, ResponseError

from src.db import redis_db

class EventHandle(object):
    def __init__(self, client = None):
        self.client = client or redis_db
        if not self.client:
            raise ValueError(f"The redis client is {self.client}")

    async def publish(self, topic: str, value: Any, **kwargs) -> bytes:
        """

        :param topic:
        :param value:
        :param kwargs:
        :return:  b'1716345367494-1'
        """
        return await self.client.xadd(topic, {"data": json.dumps(value)}, **kwargs)


class RedisPubSubHandle(EventHandle):
    """
    async def run():
        # 创建 redis 实例
        rc = aioredis.Redis(host='localhost', port=6379, db=0)
        rps = RedisPubSubHandle(rc)
        topic = "rps"
        async def callback(x):
            print(x)

        # 订阅消息, 并声明回调函数
        await rps.subscribe(callback, topic)
        await asyncio.sleep(1)

        # 推送消息
        for i in range(10):
            await rps.publish(topic, f"hello_{i}")

        await rc.aclose()
    """

    def __init__(self, client: aioredis.client.Redis):
        super(RedisPubSubHandle, self).__init__(client)

    async def subscribe(self, callback: Callable, topic: str, **kwargs) -> None:
        """

        :param callback: 回调的方法, 参数为订阅到的数据
        :param topic: 订阅的主题
        :param kwargs:
        :return:
        """
        _task = asyncio.create_task(self._recv_event(callback, topic, **kwargs))

    async def _recv_event(self, callback: Callable, topic: str, block: int = 200, last_id="$", **kwargs):
        """
        :param callback:
        :param topic:
        :param block:
        :param last_id:
        :param kwargs:
        :return:
        """
        while True:
            try:
                result = await self.client.xread(streams={topic: last_id}, block=block, **kwargs)
                if result:
                    last_id = result[0][1][-1][0]
                    for _id, value in result[0][1]:
                        await callback(json.loads(value[b"data"]))
            except Exception as e:
                traceback.print_exc()


class RedisGroupPubSubHandle(EventHandle):
    """
    async def run():
        # 创建 redis 实例
        rc = aioredis.Redis(host='localhost', port=6379, db=0)
        rgs = RedisGroupPubSubHandle(rc)

        # 推送消息
        topic = "rgs"
        group = "group"
        await rgs.group_publish(group, topic, f"hello")

        async def callback(x):
            print(x)
        # 订阅消息, 声明回调函数,  c 为消费者组的名称
        await rgs.group_subscribe(callback, "group", topic, "c")

        # 创建一些消息
        # await asyncio.sleep(1)
        # for i in range(10):
        #     await rgs.group_publish(group, topic, f"hello_{i}")
        # await asyncio.sleep(10)

        # 检查未处理的消息, 并重新分配和处理
        await rgs.check_pending_and_claim_message(callback, group, topic, "c")
        await rc.aclose()
    """

    def __init__(self, client: aioredis.client.Redis=None):
        super(RedisGroupPubSubHandle, self).__init__(client)

    async def group_publish(self, group: str, topic: str, value: Any, **kwargs):
        """
        使用消费者组发布消息
        和普通的发布订阅的区别是, redis 消费者组类似 kafka 的消费者组
            1. 可以对消费者进行负载均衡
            2. 某个消费者可以对消息进行确认, 确保消息不会重复发送, 避免了多个消费者竞争数据
            3. 消费超时的消息, 可以重新让其他消费者消费

        :param group:
        :param topic:
        :param value:
        :param kwargs:
        :return:
        """
        # 创建消费者组
        await self._create_group(group, topic, **kwargs)
        # 发布消息
        await self.publish(topic, value, **kwargs)

    async def _create_group(self, group_name: str, topic: str, **kwargs):
        """
        将 streams 和 group 绑定
        :param group_name:
        :param topic:
        :param kwargs:
        :return:
        """
        try:
            await self.client.xgroup_create(name=topic, groupname=group_name, id=0, **kwargs)
        # 重复创建会报错
        except ResponseError as e:
            pass
        except Exception as e:
            traceback.print_exc()

    async def group_subscribe(self, callback: Callable, group_name: str, topic: str, consumer_name, block=10, count=1, last_msg_id=">", **kwargs):
        _task = asyncio.create_task(self._recv_group_event(callback, group_name, topic, consumer_name, block=block, count=count, last_msg_id=last_msg_id, **kwargs))

    async def _recv_group_event(self, callback: Callable, group_name: str, topic: str, consumer_name, block=10, count=1, last_msg_id=">", **kwargs):
        """
        使用消费者组订阅消息
        :param callback:
        :param group_name:
        :param topic:
        :param consumer_name:
        :param block: 指定阻塞时间（单位为毫秒）
        :param count: 指定一次从流中读取的消息数量
        :param last_msg_id: > 表示新消息
        :param kwargs:
        :return:
        """
        while True:
            try:
                result = await self.client.xreadgroup(
                    groupname=group_name,
                    consumername=consumer_name,
                    streams={topic: last_msg_id},
                    block=block,
                    count=count,
                    **kwargs
                )
                for d_stream in result:
                    for element in d_stream[1]:
                        _id, value = element
                        try:
                            await callback(json.loads(value[b"data"]))
                            await self.client.xack(d_stream[0], group_name, _id)
                        except Exception as e:
                            pass

            except ResponseError as e:
                raise e
            except Exception as e:
                traceback.print_exc()

    async def check_pending_and_claim_message(
            self,
            callback: Callable,
            group_name: str,
            topic: str,
            consumer_name: str,
            pr_min="-",
            pr_max="+",
            pr_count=10,
            min_idle_time=60,
            interval=60,
            **kwargs
    ):
        """

        :param callback:
        :param group_name:
        :param topic:
        :param consumer_name:
        :param pr_min: 获取的 pending 消息起始 ID
        :param pr_max: 获取的 pending 消息结束 ID
        :param pr_count: 每次获取的 pending 消息数量
        :param min_idle_time: 超时秒数
        :param interval: 循环获取 pending 的间隔时间
        :param kwargs:
        :return:
        """

        async def wrap():
            while True:
                pr = await self.client.xpending_range(name=topic, groupname=group_name, min=pr_min, max=pr_max, count=pr_count)
                if pr:
                    claimed_messages = await self.client.xautoclaim(topic, group_name, consumer_name, min_idle_time, justid=False)
                    for message in claimed_messages[1]:
                        _id, data = message
                        try:
                            await callback(json.loads(data[b"data"]))
                            await self.client.xack(topic, group_name, _id)
                        except Exception as e:
                            traceback.print_exc()

                await asyncio.sleep(interval)

        _task = asyncio.create_task(wrap())

rgps = RedisGroupPubSubHandle()

if __name__ == '__main__':
    async def run1():
        rc = aioredis.Redis(host='localhost', port=6379, db=0)
        rps = RedisPubSubHandle(rc)
        topic = "rps"

        async def callback(x):
            print(x)

        await rps.subscribe(callback, topic)
        await asyncio.sleep(1)

        for i in range(10):
            await rps.publish(topic, f"hello_{i}")

        await asyncio.sleep(10)
        await rc.aclose()


    async def run2():
        rc = aioredis.Redis(host='localhost', port=6379, db=0)
        rgs = RedisGroupPubSubHandle(rc)
        topic = "rgs"
        group = "group"
        await rgs.group_publish(group, topic, f"hello")

        async def callback(x):
            print(x)

        await rgs.group_subscribe(callback, "group", topic, "c")
        await asyncio.sleep(1)
        for i in range(10):
            await rgs.group_publish(group, topic, f"hello_{i}")
        await asyncio.sleep(10)

        await rgs.check_pending_and_claim_message(callback, group, topic, "c")
        await rc.aclose()


    asyncio.run(run2())
