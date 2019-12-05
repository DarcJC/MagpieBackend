#!/usr/bin/env python
# -*- coding: utf-8 -*-

from orm import sql
import asyncio


async def test_getConnection():
    factory = sql.get_mysql_factory()
    pool = factory.get_pool(
        usr="root",
        pwd="root",
        db_name="dev",
    )
    async with sql.MySQLContextManager(pool) as context:
        cur = context.connection.cursor()
        command = "SELECT * FROM django_migrations;"
        cur.execute(command)
        res = cur.fetchall()
        print(res)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(test_getConnection())
    # unittest.main()
