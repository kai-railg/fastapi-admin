# -*- encoding: utf-8 -*-

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.oop.api_view import BaseApiView
from src.db import async_session


class ApiView(BaseApiView):
    def get(self,
            body: dict,
            session: AsyncSession = Depends(dependency=async_session),):
        return
