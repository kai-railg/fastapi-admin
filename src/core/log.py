# -*- encoding: utf-8 -*-

import os
import sys

from loguru import logger

LOG_DIR = "./log"


# 用于区分不同的日志句柄
def log_name_filter(**kwargs):
    def is_log_name(record):

        extra_data: dict = record["extra"]

        for k, v in kwargs.items():
            if extra_data.get(k) != v:
                return False
        return True

    return is_log_name

# 自定义格式函数, 可以根据上下文数据区分日志格式
def custom_format(record) -> str:
    extra_data = record["extra"] or {}
    format_str = f"{record['time']:YYYY-MM-DD > HH:mm:ss.SSS > zz WeekE} | {record['level'].name} | {record['message']}"

    # fmd: format_map_data
    fmd_list = []
    for k, v in extra_data.items():
        if k == "log_name":
            continue
        fmd_list.append(f"{k}={v}")

    if fmd_list:
        format_str += f" | {','.join(fmd_list)}"
    return format_str + "\n"


# 配置日志格式和级别
logger_config = dict(
    rotation="1 day",
    retention="45 days",
    # 更多格式设置指令 https://loguru.readthedocs.io/en/stable/api/logger.html#record
    # format="{time:YYYY-MM-DD > HH:mm:ss.SSS > zz WeekE} | {level} | {message}",
    format=custom_format,
    # 压缩格式
    compression="gz",
    # 采用布尔值，并确定是否应启用终端着色。
    colorize=True,
    # 如果设置为 True，则会导致日志记录以 JSON 格式显示。
    # 每条记录中的信息都将以键/值对的形式提供
    serialize=False,
    # 确定异常跟踪是否应延伸到捕获错误的点之外，以便更易于调试。
    backtrace=True,
    # 确定变量值是否应在异常跟踪中显示。在生产环境中，应将其设置为 False，以避免敏感信息泄露
    diagnose=False,
    # 默认情况下，添加到记录器的所有接收器都是线程安全的。它们不是多进程安全的.
    # 启用此选项会将日志记录置于队列中，以避免在多个进程记录到同一目标时发生冲突。
    enqueue=False,
    # 如果在记录到指定的接收器时发生意外错误，您可以通过将此选项设置为 True 来捕获该错误。错误将被打印为标准错误。
    catch=True
)

# bk: bind_kwargs
def get_logger(log_name: str, bk=None, **kwargs):

    log_file = f"{LOG_DIR}/{log_name.strip('/')}.log"

    log_path = "/".join(log_file.split("/")[:-1])
    if not os.path.exists(log_path):
        os.makedirs(log_path, exist_ok=True)

    bk = {**(bk or {}), "log_name": log_name}

    logger.add(
        log_file,
        filter=log_name_filter(**bk),
        **{
            **logger_config,
            **kwargs
        })

    return logger.bind(**bk)


def patching(record):
    # 避免如下代码的报错
    # print("message is {'key': 'value'}".format_map({}))
    record['message'] = record['message'].replace("{", "{{").replace("}", "}}")


logger = logger.patch(patching)
logger.remove(0)
logger.add(sys.stderr, level="ERROR")
logger.add(f"{LOG_DIR}/console.log", level="DEBUG")

# fastapi_log
f_log = get_logger("f_log")
request_post_log = get_logger("request_post")
request_get_log = get_logger("request_get")
request_send_log = get_logger("request_send")
dao_log = get_logger("dao")
websocket_log = get_logger("websocket")
broad_log = get_logger("broad")

# 不同level
# logger.trace("A trace message.")
# logger.debug("A debug message.")
# logger.info("An info message.")
# logger.success("A success message.")
# logger.warning("A warning message.")
# logger.error("An error message.")
# logger.critical("A critical message.")

# 创建自定义级别
# logger.level("FATAL", no=60, color="<red>", icon="!!!")
# logger.log("FATAL", "A user updated some information.")

# 日志上下文
# childLogger = logger.bind(seller_id="001", product_id="123")
# childLogger.info("product page opened")
# childLogger.info("product updated")
# childLogger.info("product page closed")

# 记录错误
# with logger.catch():
#     50 / x
# 或者使用
# @logger.catch(level="ERROR", message="An error caught in test()")

# 集中和监控日志
# https://betterstack.com/logtail

# 更多信息
# https://betterstack.com/community/guides/logging/loguru/

# if __name__ == "__main__":
#     f_log = get_logger("f_log")
#     f_log.info("f_log")

#     request_post_log = get_logger("request_post")

#     with request_post_log.contextualize(vehicle_id="001"):
#         request_post_log.error("request_post_log")

#     request_get_log = get_logger("request_get", bk={"vehicle_id": "002"})
#     request_get_log.error("request_get_log")

#     request_get_log = get_logger("request_get", bk={"vehicle_id": "003"})
#     request_get_log.error("request_get_log")
