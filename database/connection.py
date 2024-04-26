import asyncpg

from config import (
    DATABASE,
    HOST,
    PASSWORD,
    PORT,
    USER,
    log,
)
from database import (
    queries,
)

class Db:
    def __init__(self):
        self.pool = None

    async def init_pool(self):
        self.pool = await asyncpg.create_pool(
            database=DATABASE,
            user=USER,
            host=HOST,
            port=PORT,
            password=PASSWORD,
        )
        log.info(" Есть коннект к базе")

    async def add_raffle(
        self,
        user_id: int | None,
        user_login: str | None,
        user_name: str | None,
        chat_id: int | None,
    ) -> None:
        async with self.pool.acquire() as con:
            async with con.transaction():
                id_ = await con.fetchval(queries.insert_raffle, user_id, user_login, user_name, chat_id)
                log.info(
                    f" Создана запись user_id={user_id} id={id_}, user_login={user_login}, user_name={user_name}"
                )

    async def add_shrit(self, user_id: int | None, shirt: str | None) -> None:
        async with self.pool.acquire() as con:
            async with con.transaction():
                id_ = await con.fetchval(queries.insert_field.format(field="shirt"), user_id, shirt)
                log.info(
                    f" Пользователь user_id={user_id} id={id_} добавил футболку {shirt}"
                )

    async def add_size(self, user_id: int | None, size: str | None) -> None:
        async with self.pool.acquire() as con:
            async with con.transaction():
                id_ = await con.fetchval(queries.insert_field.format(field="size"), user_id, size)
                log.info(
                    f" Пользователь user_id={user_id} id={id_} добавил размер {size}"
                )

    async def aprove(self, id_: int | str):
        async with self.pool.acquire() as con:
            async with con.transaction():
                id_ = await con.fetchval(queries.update_status, int(id_))
                log.info(
                    f" Пользователь id={id_} подтвердил статус оплаты"
                )
                return id_

    async def add_identification(self, user_id: int | None, identification: str | None) -> None:
        async with self.pool.acquire() as con:
            async with con.transaction():
                id_ = await con.fetchval(queries.insert_field.format(field="identification"), user_id, identification)
                log.info(
                    f" Пользователь user_id={user_id} id={id_} добавил свои данные {identification}"
                )

    async def get_chat_id(self, id_: int) -> int:
        async with self.pool.acquire() as con:
            async with con.transaction():
                chat_id = await con.fetchval(queries.select_chat_id, id_)
                log.info(
                    f" Пользователь chat_id={chat_id} id={id_} подтвердил заказ"
                )
                return chat_id

    async def add_document(
        self,
        user_id: int,
        document_id: str | None,
        photo_id: str | None,
        video_id: str | None,
    ) -> None:
        async with self.pool.acquire() as con:
            async with con.transaction():
                await con.execute(queries.insert_document, user_id, document_id, photo_id, video_id)
        log.info(
            f" Добавлен документ user_id={user_id} document_id={document_id} photo_id={photo_id} video_id={video_id}"
        )

    async def get_order(self, user_id: int | None) -> None:
        async with self.pool.acquire() as con:
            async with con.transaction():
                order = await con.fetchrow(queries.select_order, user_id)
                log.info(
                    f" Пользователь user_id={user_id} id={order['id']} оформил заказ"
                )
                return order

    async def get_documents(self, user_id: int) -> tuple[set, set, set]:
        pics = set()
        docs = set()
        videos = set()
        async with self.pool.acquire() as con:
            async with con.transaction():
                pics_docs_and_videos = await con.fetch(queries.select_documents, user_id)

                if pics_docs_and_videos:
                    pics.update(pics_docs_and_videos[0][0])
                    docs.update(pics_docs_and_videos[0][1])
                    videos.update(pics_docs_and_videos[0][2])

                    if None in pics:
                        pics.remove(None)

                    if None in docs:
                        docs.remove(None)

                    if None in videos:
                        videos.remove(None)

        log.info(f" Для пользователя user_id={user_id} получено {len(docs)} документов, "
                        f"{len(videos)} видео и {len(pics)} фото")

        return pics, docs, videos

    async def get_report(self, user_id: int):
        async with self.pool.acquire() as con:
            async with con.transaction():
                report = await con.fetch(queries.select_report)
                log.info(
                    f" Получен отчет пользователем {user_id}"
                )
                return report


async def init_db() -> Db:
    db = Db()
    await db.init_pool()

    async with db.pool.acquire() as con:
        async with con.transaction():
            await con.execute(queries.create_raffle)
            await con.execute(queries.migration)

    return db
