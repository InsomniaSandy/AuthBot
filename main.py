import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import config
import db

bot = Bot(
    token=config.TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()


# ---------------- FSM SETUP ----------------
class Setup(StatesGroup):
    name = State()
    link = State()


# ---------------- START SETUP ----------------
@dp.message(F.text == "/setup")
async def setup_start(message: Message, state: FSMContext):
    await message.answer("👤 Введи имя админа:")
    await state.set_state(Setup.name)


@dp.message(Setup.name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("🔗 Введи ссылку (https://t.me/username):")
    await state.set_state(Setup.link)


@dp.message(Setup.link)
async def get_link(message: Message, state: FSMContext):
    data = await state.get_data()

    await db.set_settings(
        chat_id=message.chat.id,
        name=data["name"],
        link=message.text
    )

    await message.answer("✅ Настроено! Бот активирован.")
    await state.clear()


# ---------------- MESSAGE MIRROR ----------------
async def send_with_signature(message: Message, name: str, link: str):
    sig = f"\n\n━━━━━━━━━━━━\n👤 {name}\n🔗 {link}"

    if message.text:
        await message.answer(message.text + sig)

    elif message.photo:
        await message.answer_photo(
            message.photo[-1].file_id,
            caption=(message.caption or "") + sig
        )

    elif message.video:
        await message.answer_video(
            message.video.file_id,
            caption=(message.caption or "") + sig
        )

    elif message.document:
        await message.answer_document(
            message.document.file_id,
            caption=(message.caption or "") + sig
        )

    elif message.audio:
        await message.answer_audio(
            message.audio.file_id,
            caption=(message.caption or "") + sig
        )

    elif message.voice:
        await message.answer_voice(message.voice.file_id)

        await message.answer(sig)

    elif message.animation:
        await message.answer_animation(
            message.animation.file_id,
            caption=(message.caption or "") + sig
        )

    elif message.sticker:
        await message.answer_sticker(message.sticker.file_id)
        await message.answer(sig)


# ---------------- MAIN HANDLER ----------------
@dp.message()
async def handler(message: Message):
    if not message.chat or message.chat.type not in ["group", "supergroup"]:
        return

    if message.from_user and message.from_user.is_bot:
        return

    settings = await db.get_settings(message.chat.id)

    if not settings:
        return

    name, link = settings

    try:
        await send_with_signature(message, name, link)
        await message.delete()
    except Exception as e:
        print("Error:", e)


# ---------------- START ----------------
async def main():
    await db.init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
