# -*- coding: utf-8 -*-

"""
This file is part of Magpie OnlineJudge Project
Authors: DarcJC
"""
from functools import wraps
from abc import ABCMeta, abstractmethod
import pymysql
import asyncio


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
        return await _get()

    def release_connection(self, connection_id: int) -> None:
        if connection_id >= self.max_connection:
            raise IndexError("Id is too large.")
        (con, _) = self._connections
        self._connections[connection_id] = (con, False)


class MySQLContextManager:
    def __init__(self, pool: MySQLPool):
        self.pool = pool

    def __enter__(self):
        self.connection, self.conn_id = self.pool.get_connection()
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.pool.release_connection(self.conn_id)
        return True


class SQLObject(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self):
        """
        Create the sql connector pool
        """
        pass

    @abstractmethod
    def exec(self, sql: str):
        pass
