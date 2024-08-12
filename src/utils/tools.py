# -*- encoding: utf-8 -*-

import datetime


diff = datetime.datetime.now() - datetime.datetime.utcnow()
hours = round(diff.days * 24 + diff.seconds / 3600)
tz = datetime.timezone(datetime.timedelta(hours=hours))


def get_now_datetime() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_now_datetime_with_tz() -> str:
    """2022-05-20T02:38:58.350000+08:00"""
    return datetime.datetime.now(tz=tz).isoformat()
