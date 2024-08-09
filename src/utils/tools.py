# -*- encoding: utf-8 -*-

import datetime

def get_now_datetime() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
