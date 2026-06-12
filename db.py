import aiosqlite

DB_NAME = "bot.db"


async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            chat_id INTEGER PRIMARY KEY,
            admin_name TEXT,
            admin_link TEXT
        )
        """)
        await db.commit()


async def set_settings(chat_id: int, name: str, link: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        INSERT INTO settings(chat_id, admin_name, admin_link)
        VALUES(?, ?, ?)
        ON CONFLICT(chat_id)
        DO UPDATE SET admin_name=excluded.admin_name,
                      admin_link=excluded.admin_link
        """, (chat_id, name, link))
        await db.commit()


async def get_settings(chat_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT admin_name, admin_link FROM settings WHERE chat_id=?",
            (chat_id,)
        )
        return await cursor.fetchone()
