import os
import aiohttp
import asyncio
import requests
import tempfile
from bs4 import BeautifulSoup
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Allowed Users - keep default values
ALLOWED_USERS = {"1557539460", "6667553516", "5725206423"}

bot = Client("anime_multporn_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# User session storage
USER_SELECTION = {}

async def fetch_anime_info(anime_name):
    url = "https://graphql.anilist.co/"
    query = '''
    query ($search: String) {
        Media(search: $search, type: ANIME) {
            id
            title {
                romaji
                english
            }
            episodes
            genres
            coverImage {
                extraLarge
            }
        }
    }
    '''
    variables = {"search": anime_name}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={"query": query, "variables": variables}) as response:
            data = await response.json()
            return data.get("data", {}).get("Media")

def scrape_images(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None, "Failed to fetch the page."

    soup = BeautifulSoup(response.text, "html.parser")
    image_tags = soup.find_all("img")

    image_urls = []
    for img in image_tags:
        src = img.get("src")
        if src and (".jpg" in src or ".png" in src or ".jpeg" in src):
            image_urls.append(src if src.startswith("http") else "https://multporn.net" + src)

    return image_urls, None if image_urls else "No images found."

def download_image(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, stream=True)
    if response.status_code == 200:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        with open(temp_file.name, "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        return temp_file.name
    return None

@bot.on_message(filters.command("start"))
async def start(client, message):
    user_id = str(message.from_user.id)
    if user_id not in ALLOWED_USERS:
        await message.reply_text("🚫 You are not authorized to use this bot.")
        return
    await message.reply_text("Welcome! Use **/anime** to search for anime info or send a Multporn.net link to fetch images.")

@bot.on_message(filters.command("anime"))
async def anime(client, message):
    user_id = str(message.from_user.id)
    if user_id not in ALLOWED_USERS:
        await message.reply_text("🚫 You are not authorized to use this bot.")
        return
    await message.reply_text("📩 Send me the anime name:")
    USER_SELECTION[message.chat.id] = {"anime_name": None, "quality": None, "format": None}

@bot.on_message(filters.text & filters.private)
async def handle_text(client, message):
    chat_id = message.chat.id
    user_id = str(message.from_user.id)
    if user_id not in ALLOWED_USERS:
        await message.reply_text("🚫 You are not authorized to use this bot.")
        return

    text = message.text.strip()

    if text.startswith("https://multporn.net/"):
        await message.reply_text("Fetching images, please wait...")
        image_urls, error = scrape_images(text)

        if error:
            await message.reply_text(f"Error: {error}")
            return

        for img_url in image_urls:
            img_path = download_image(img_url)
            if img_path:
                await client.send_document(message.chat.id, img_path)
                os.remove(img_path)

        await message.reply_text("All images have been uploaded!")

    elif chat_id in USER_SELECTION and USER_SELECTION[chat_id]["anime_name"] is None:
        anime_name = text
        USER_SELECTION[chat_id]["anime_name"] = anime_name

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("480p", callback_data="480p")],
            [InlineKeyboardButton("720p", callback_data="720p")],
            [InlineKeyboardButton("1080p", callback_data="1080p")],
            [InlineKeyboardButton("720p & 1080p", callback_data="720p_1080p")],
            [InlineKeyboardButton("480p, 720p & 1080p", callback_data="480p_720p_1080p")]
        ])

        await message.reply_text("📊 Choose quality:", reply_markup=keyboard)

@bot.on_callback_query()
async def button_callback(client, callback_query):
    chat_id = callback_query.message.chat.id
    data = callback_query.data
    user_id = str(callback_query.from_user.id)

    if user_id not in ALLOWED_USERS:
        await callback_query.answer("🚫 You are not authorized to use this bot.")
        return

    if chat_id not in USER_SELECTION:
        await callback_query.answer("❌ No active selection found.")
        return

    if data in ["480p", "720p", "1080p", "720p_1080p", "480p_720p_1080p"]:
        USER_SELECTION[chat_id]["quality"] = data.replace("_", ", ")

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Otaku", callback_data="otaku")],
            [InlineKeyboardButton("Hanime", callback_data="hanime")],
            [InlineKeyboardButton("Ongoing", callback_data="ongoing")]
        ])

        await callback_query.message.reply_text("📁 Choose format:", reply_markup=keyboard)

    elif data in ["otaku", "hanime"]:
        anime_name = USER_SELECTION[chat_id]["anime_name"]
        quality = USER_SELECTION[chat_id]["quality"] or "Unknown"

        anime = await fetch_anime_info(anime_name)
        if not anime:
            await callback_query.message.reply_text("❌ Anime not found.")
            return

        anime_id = anime["id"]
        image_url = f"https://img.anili.st/media/{anime_id}"
        title = anime["title"]["english"] or anime["title"]["romaji"]
        genres_text = ", ".join(anime["genres"])
        genre_tags = " ".join([f"#{g}" for g in anime["genres"]])

        if data == "hanime":
            message_text = f"<b>💦 {title}\n╭──────────────────────\n├ 📺 Episode : {anime['episodes'] or 'N/A'}\n├ 💾 Quality : {quality}\n├ 🎭 Genres: {genres_text}\n├ 🔊 Audio track : Sub\n├ #Censored\n├ #Recommendation +++++++\n╰──────────────────────</b>"
        else:
            message_text = f"""<b>💙 {title}</b>

<b>🎭 Genres :</b> {genres_text}
<b>🔊 Audio :</b> Dual Audio
<b>📡 Status :</b> Completed
<b>🗓 Episodes :</b> {anime['episodes'] or 'N/A'}
<b>💾 Quality :</b> {quality}
<b>✂️ Sizes :</b> 50MB, 120MB & 300MB
<b>🔞 Rating :</b> PG-13

<blockquote>📌 : {genre_tags}</blockquote>"""

        await callback_query.message.reply_photo(photo=image_url, caption=message_text, parse_mode=ParseMode.HTML)

    elif data == "ongoing":
        anime_name = USER_SELECTION[chat_id]["anime_name"]
        quality = USER_SELECTION[chat_id]["quality"] or "Unknown"

        anime = await fetch_anime_info(anime_name)
        if not anime:
            await callback_query.message.reply_text("❌ Anime not found.")
            return

        anime_id = anime["id"]
        image_url = f"https://img.anili.st/media/{anime_id}"
        title = anime["title"]["english"] or anime["title"]["romaji"]
        genres_text = ", ".join(anime["genres"])

        message_text = f"""❤️  {title}
╭───────────────────
├ 📺 Episodes : {anime['episodes'] or 'N/A'}
├ 💾 Quality : {quality}
├ 🎭 Genres: {genres_text}
├ 🔊 Audio track : Dual [English+Japanese]
╰───────────────────
Report Missing Episodes: @Otaku_Library_Support_Bot"""

        await callback_query.message.reply_photo(photo=image_url, caption=message_text, parse_mode=ParseMode.HTML)

print("✅ Bot is running...")
if __name__ == "__main__":
    bot.run()
