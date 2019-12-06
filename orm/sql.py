# -*- coding: utf-8 -*-

"""
This file is part of Magpie OnlineJudge Project
Authors: DarcJC
"""
from functools import wraps
from abc import ABCMeta, abstractmethod
import pymysql
import asyncio
import typing

_LIMIT_TYPE = typing.TypeVar("_LIMIT_TYPE", str, range)


class MySQLFactory:
    def __init__(self):
        self.pools: dict = {}

    def get_pool(self, usr: str, pwd: str, db_name: str, host: str = "localhost", port: int = 3306):
        url: str = f"mysql://{host}:{port}/{db_name}?user={usr}&password={pwd}"
        if self.pools.get(str(url.__hash__()), None):
            return self.pools.get(url, None)
        pool = MySQLPool(
            usr=usr,
            pwd=pwd,
            db_name=db_name,
            host=host,
            port=port,
        )
        self.pools[url.__hash__()] = pool
        return pool


class MySQLPool(object):
    def __init__(self, usr: str, pwd: str, db_name: str, host: str = "localhost", port: int = 3306,
                 max_connection: int = 4):
        if max_connection <= 0:
            raise NotImplementedError("max connection could not <= 0")
        self._connections: list = []
        self.max_connection = max_connection
        self.usr = usr
        self.pwd = pwd
        self.db_name = db_name
        self.host = host
        self.port = port
        for _ in range(0, max_connection):
            self._connections.append((pymysql.connect(
                host=host,
                user=usr,
                password=pwd,
                port=port,
                database=db_name,
                charset="utf8mb4",
                use_unicode=True,
            ), False))

    async def get_connection(self) -> (object, int):
        async def _get():
            while True:
                for i in range(0, self.max_connection):
                    (con, lock) = self._connections[i]
                    if not lock:
                        return con, i
                await asyncio.sleep(0.1)

        connection, index = await _get()
        if not connection.open:
            connection = self._connections[index] = (pymysql.connect(
                host=self.host,
                user=self.usr,
                password=self.pwd,
                port=self.port,
                database=self.db_name,
                charset="utf8mb4",
                use_unicode=True,
            ), False)
        return connection, index

    def release_connection(self, connection_id: int) -> None:
        if connection_id >= self.max_connection:
            raise IndexError("Id is too large.")
        (con, _) = self._connections[connection_id]
        self._connections[connection_id] = (con, False)


class MySQLContextManager:
    def __init__(self, pool: MySQLPool):
        self.pool = pool

    async def __aenter__(self):
        self.connection, self.conn_id = await self.pool.get_connection()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.pool.release_connection(self.conn_id)
        return True


class MySQLCommand(object):
    _SELECT = "SELECT"
    _FROM = "FROM"
    _LIMIT = "LIMIT"

    def __init__(self):
        self.command: str = ""

    def exec(self, pool: MySQLPool):
        pass

    def SELECT(self, what: str):
        self.command = self.command.join(f"{self._SELECT} {what}")

    def FROM(self, where: str):
        self.command = self.command.join(f"{self._FROM} {where}")

    def LIMIT(self, what: _LIMIT_TYPE):
        if isinstance(what, str):
            self.command = self.command.join(f"{self._LIMIT} {what}")
        else:
            self.command = self.command.join(f"{self._LIMIT} {what.start},{what.stop}")

    def WHERE(self, where: str):
        self.command = self.command.join(f"{self._FROM} {where}")


_MYSQL_FACTORY = MySQLFactory()


def get_mysql_factory():
    return _MYSQL_FACTORY
