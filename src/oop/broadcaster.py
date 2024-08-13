import asyncio
import json
import time
import traceback
from asyncio import Queue

from src.core import broad_log, BROADCASTER_TYPE
from src.db import redis_db


class BroadCaster(object):
    def __init__(self, topic) -> None:
        self.topic = topic
        self.queue_recv = Queue()
        self.queue_send = Queue()

    async def get(self):
        mess = await self.queue_recv.get()
        return mess

    async def put(self, data):
        return await self.queue_send.put(data)


class BroadCasterNoPub(BroadCaster):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.exchange_name = self.topic
        asyncio.create_task(self.__pub_event())

    # 不进行消息分发，直接打通 queue_send 和 queue_recv 即可
    async def __pub_event(self):
        while True:
            mess = await self.queue_send.get()
            await self.queue_recv.put(mess)


class BroadCasterRedis(BroadCaster):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.redis  = redis_db
        asyncio.create_task(self.__pub_event())
        asyncio.create_task(self.__recv_event())

    async def __pub_event(self):
        while True:
            mess = await self.queue_send.get()
            try:
                broad_log.info(f"Publish message, {mess}, {self.queue_send.qsize()}")
                t1 = time.time()
                await self.redis.xadd(self.topic, {"data": json.dumps(mess)}, maxlen=1000)
                t2 = time.time()
                if t2 - t1 > 800:
                    broad_log.warning(f"Save redis xadd function used time is, {t2 - t1} ms")
            except Exception as ex:
                broad_log.error(f"publish error: {traceback.format_exc()}")

    async def __recv_event(self):
        """
        result: [[b'key', [(b'1711434977729-4', {b'data': b'{"987": "987"}'})]]]
        """
        last_id = "$"
        while True:
            try:
                result = await self.redis.xread(streams={self.topic: last_id}, block=200)
                if result:
                    last_id = result[0][1][-1][0]
                    for _id, value in result[0][1]:
                        value = json.loads(value[b"data"])
                        broad_log.info(f"Receive message, {value}")
                        await self.queue_recv.put(value)
            except Exception as ex:
                broad_log.error(f"receive error: {traceback.format_exc()}")


BroadCasterCls = None
if BROADCASTER_TYPE == "nopub":
    BroadCasterCls = BroadCasterNoPub
elif BROADCASTER_TYPE == "redis":
    BroadCasterCls = BroadCasterRedis

if BroadCasterCls is None:
    raise Exception(f"BroadCasterCls is None, BROADCASTER_TYPE is {BROADCASTER_TYPE}, must be nopub or redis")