# -*- encoding: utf-8 -*-


# -*- coding: utf-8 -*-
"""
@Version : python3.9
@Time    : 2023/12/8 2:19 PM
@Author  : kai.wang
@Email   : kai.wang@westwell-lab.com
"""
from typing import List
from contextlib import asynccontextmanager

import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import ScalarResult, insert, select, update, delete
from sqlalchemy.orm import selectinload, make_transient

from src.core import dao_log

catch = dao_log.catch


class DatabaseAccessObjects(object):

    # -> Any | ScalarResult | None:
    @catch
    async def get_scalars_by_orm(self, orm, session: AsyncSession, **kwargs):
        """
            ScalarResult:
                .first()
                .scalar_one_or_none()
        """
        result = await session.execute(orm)
        if kwargs.get("first", False):
            return result.scalar_one_or_none()
        return result.scalars()

    @catch
    async def insert(self, table, values: dict, session: AsyncSession):
        stmt = insert(table).values(**values)
        return await session.execute(stmt)

    @catch
    async def bulk_insert(self, table, data_list: List, session: AsyncSession):

        stmt = insert(table)
        return await session.execute(stmt, data_list)

    @catch
    async def update(self, table, conditions: List, values: dict, session: AsyncSession):
        stmt = update(table).where(*conditions).values(**values)
        return await session.execute(stmt)

    @catch
    async def select(
            self,
            table,
            conditions: tuple,
            session: AsyncSession,
            **kwargs) -> ScalarResult:
        orm = select(table).where(*conditions)
        return await self.get_scalars_by_orm(orm, session, **kwargs)

    @catch
    async def query_with_options(
            self,
            table,
            option,
            conditions: tuple,
            session: AsyncSession,
            **kwargs) -> ScalarResult:
        orm = select(table).options(selectinload(option)).where(*conditions)
        return await self.get_scalars_by_orm(orm, session, **kwargs)

    @catch
    async def delete_with_conditions(self, table, conditons, session: AsyncSession):
        await session.scalars(
            delete(table).where(
                *conditons
            )
        )
        await session.flush()

    @catch
    async def delete_instance(self, instance, session: AsyncSession):
        await session.delete(instance)
        await session.flush()

    @catch
    async def truncate(self, instance, session: AsyncSession):
        await session.execute(
            sqlalchemy.text(f"TRUNCATE TABLE {instance.__tablename__}")
        )

    @catch
    async def get_condition_or(self, conditions: List):
        return sqlalchemy.or_(*conditions)

    @catch
    async def get_condition_in(self, column: sqlalchemy.Column, other: List):
        return column.in_(other)

    # 先将某个对象移除再恢复, 期间自定义操作

    @catch
    @asynccontextmanager
    async def make_transient(self, instance, session: AsyncSession):

        # 先删除这个对象，确保不会被查询到
        await session.delete(instance)
        await session.flush()
        yield
        # 将这个对象转为瞬态，相当于复制了一份，然后再将入到session中
        make_transient(instance)
        session.add(instance)


dao = DatabaseAccessObjects()


# from sqlalchemy import select
#
# async def  fetch_data(session):
#     result = await session.execute(select(User).where(User.id == 1))
#     user = result.scalar()
#     return user

# from sqlalchemy import insert
#
# async def  insert_data(session, username, email):
#     stmt = insert(User).values(username=username, email=email)
#     await session.execute(stmt)
#     await session.commit()


# 异步查询数据:
#
# from sqlalchemy import select
#
#
# async def  fetch_data(session):
#     result = await session.execute(select(User).where(User.id == 1))
#     user = result.scalar()
#     return user
#
#
# 异步插入数据:
#
# from sqlalchemy import insert
#
#
# async def insert_data(session, username, email):
#     stmt = insert(User).values(username=username, email=email)
#     await session.execute(stmt)
#     await session.commit()
#
#
# 异步更新数据:
#
# from sqlalchemy import update
#
#
# async def  update_data(session, user_id, new_username):
#     stmt = update(User).where(User.id == user_id).values(username=new_username)
#     await session.execute(stmt)
#     await session.commit()
#
#
# 异步删除数据:
#
# from sqlalchemy import delete
#
#
# async def  delete_data(session, user_id):
#     stmt = delete(User).where(User.id == user_id)
#     await session.execute(stmt)
#     await session.commit()
#
#
# 异步批量插入数据:
#
# from sqlalchemy import insert
#
#
# async def  bulk_insert_data(session, data_list):
#     data_list = [
#         {'username': 'user1', 'email': 'user1@example.com'},
#         {'username': 'user2', 'email': 'user2@example.com'},
#         # 添加更多数据...
#     ]
#     stmt = insert(User)
#     await session.execute(stmt, data_list)
#     await session.commit()
#
#
# 请注意，在异步环境中，await session.commit()
# 通常用于提交事务。异步操作涉及到协程和事件循环，确保你的代码运行在异步上下文中，例如使用
# async with Session() as session 确保你的会话是异步的。
