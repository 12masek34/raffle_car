import asyncpg

import config
from database import (
    queries,
)


class Db:
    def __init__(self):
        self.pool = None

    async def init_pool(self):
        self.pool = await asyncpg.create_pool(
            database=config.DATABASE,
            user=config.USER,
            host=config.HOST,
            port=config.PORT,
            password=config.PASSWORD,
        )
        config.log.info(" Есть коннект к базе")

    # async def add_car(self, user_id: int | None, user_login: str | None, user_name: str | None) -> None:
    #     async with self.pool.acquire() as con:
    #         async with con.transaction():
    #             id_ = await con.fetchval(queries.insert_car, user_id, user_login, user_name)
    #             config.log.info(
    #                 f" Создана запись user_id={user_id} id={id_}, user_login={user_login}, user_name={user_name}"
    #             )



async def init_db() -> Db:
    db = Db()
    await db.init_pool()

    async with db.pool.acquire() as con:
        async with con.transaction():
            await con.execute(queries.create_raffle)

    return db
