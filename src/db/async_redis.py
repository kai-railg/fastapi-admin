# -*- encoding: utf-8 -*-

from redis import asyncio as aioredis

from src.core import (
    REDIS_CONNECT_TYPE,
    REDIS_HOST,
    REDIS_PORT,
    REDIS_DB,
    REDIS_PASSWORD,
    REDIS_SENTINELS,
    REDIS_SENTINEL_MASTER,
)


redis_db: aioredis.Redis = None

match REDIS_CONNECT_TYPE:
    case "redis":
        redis_db = aioredis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password=REDIS_PASSWORD)
    case "redis_sentinel":
        redis_db = aioredis.sentinel.Sentinel(
            [hp.split(',') for hp in REDIS_SENTINELS.split(";")]
        ).master_for(
            REDIS_SENTINEL_MASTER,
            **{"password": REDIS_PASSWORD, "port": REDIS_PORT, "db": REDIS_DB}
        )

    case _:
        raise ValueError("REDIS_CONNECT_TYPE must be redis or redis_sentinel")
