# -*- encoding: utf-8 -*-


from typing import Any
from pydantic import BaseModel, Field, model_validator

class RequestBodySchema(BaseModel):
    """
    请求体
    """
    pass

class ResponseBodySchema(BaseModel):
    """
    响应体
    """
    code: int = Field(default=200, description="响应码")
    data: Any = Field(default={}, description="响应数据")
    message: str = Field(default="success", description="响应消息")

    # @model_validator(mode="after")
    # def after_model_validator(self):
    #     if isinstance(self.data, BaseModel):
    #         self.data = self.data.model_dump()


class StdRes(BaseModel):
    data: Any = Field(default={}, description="响应码")
    code: int = Field(default=200, description="响应码")
    msg: str = Field(default="success", description="响应消息")