# bot.py

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from config import *
import requests
import re

bot = Client("Rozibot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

user_movie_selection = {}

def shrink_link(long_url):
    api_url = f"https://shrinkme.io/api?api={SHRINKME_API}&url={long_url}"
    res = requests.get(api_url).json()
    return res.get("shortenedUrl")

@bot.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("🎬 Welcome to Rozi Movie Bot!\nSend me a movie name here after clicking the button in group.")

@bot.on_message(filters.text & filters.group)
async def handle_group_search(client, message: Message):
    if not message.text:
        return
    
    movie_name = message.text.strip()
    response = await client.send_message(SOURCE_BOT, movie_name)
    await response.delete()

    await message.reply(f"🔍 Searching for: {movie_name}\n\n⏳ Please wait...")

@bot.on_message(filters.text & filters.private)
async def handle_private_message(client, message: Message):
    user_id = message.from_user.id
    query = message.text.strip()
    
    if user_id in user_movie_selection:
        file_id = user_movie_selection[user_id]
        await client.send_document(chat_id=user_id, document=file_id)
        del user_movie_selection[user_id]
        return

    msg = await client.send_message(SOURCE_BOT, query)
    await msg.delete()
    
    async for m in client.get_chat_history(SOURCE_BOT, limit=5):
        if query.lower() in m.text.lower():
            buttons = []
            matches = re.findall(r"(\d+\.\d+ GB|\d+ MB).*?\[(.*?)\]", m.text, re.IGNORECASE)
            for idx, (size, title) in enumerate(matches, 1):
                btn = InlineKeyboardButton(
                    text=f"{idx}. {title} ({size})",
                    callback_data=f"get_{idx}"
                )
                buttons.append([btn])
            await message.reply(
                f"📂 Here is what I found for **{query}**:",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            break

@bot.on_callback_query()
async def callback_handler(client, callback_query):
    user_id = callback_query.from_user.id
    movie_index = callback_query.data.split("_")[1]

    dummy_file_id = "BQACAgUAAxkBAA..."  # Replace with your file_id list logic if storing
    user_movie_selection[user_id] = dummy_file_id
    
    long_url = f"https://t.me/{bot.me.username}?start=verify_{movie_index}_{user_id}"
    short_url = shrink_link(long_url)
    
    await callback_query.message.reply(
        f"✅ Click to verify and unlock your movie:\n{short_url}"
    )

bot.run()
