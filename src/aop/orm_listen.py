# -*- encoding: utf-8 -*-

from sqlalchemy import event
from sqlalchemy.sql import Select, Update, Delete, Insert
from sqlalchemy.sql.elements import TextClause

from src.db import pg_async_engine


# @event.listens_for(pg_async_engine, 'before_execute', retval=True)
# def before_execute(conn, clause_element, multi_params, params, execution_options):
#     # <sqlalchemy.engine.base.Connection object at 0x1033fe150> <class 'sqlalchemy.engine.base.Connection'>
#     # INSERT INTO persons (id, name) VALUES (:id, :name) <class 'sqlalchemy.sql.dml.Insert'>
#     # [{'name': 'John'}, {'name': 'Alice'}] <class 'list'>
#     # {} <class 'dict'>
#     if isinstance(clause_element, Select):
#         # 执行查询缓存操作
#         return


# @event.listens_for(pg_async_engine, 'after_execute')
# def after_execute(conn, clause_element, multi_params, params, execution_options, result, **kwargs):
#     # <sqlalchemy.engine.base.Connection object at 0x1078f5d10> <class 'sqlalchemy.engine.base.Connection'>
#     # INSERT INTO persons (id, name) VALUES (:id, :name) <class 'sqlalchemy.sql.dml.Insert'>
#     # [{'name': 'John'}, {'name': 'Alice'}] <class 'list'>
#     # {} <class 'dict'>
#     # <sqlalchemy.engine.cursor.CursorResult object at 0x107843d90> <class 'sqlalchemy.engine.cursor.CursorResult'>
#     # {}
#     for cls in [Insert, Update, Delete, TextClause]:
#         if isinstance(clause_element, cls):
#             # 执行数据更新后的操作
#             pass

# @event.listens_for(Container_data, "after_insert")
# @event.listens_for(Container_data, "after_delete")
# @event.listens_for(Container_data, "after_update")
# def after_flush(mapper, connection, target):
#     # Mapper[Container_data(container_data)] <class 'sqlalchemy.orm.mapper.Mapper'>
#     # <sqlalchemy.engine.base.Connection object at 0x110477710> <class 'sqlalchemy.engine.base.Connection'>
#     # <src.db.models.container_data.Container_data object at 0x10fe57810> <class 'src.db.models.container_data.Container_data'>
#     # 执行数据更新后的操作
#     pass
