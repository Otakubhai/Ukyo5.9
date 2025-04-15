"""
Anime Multporn Bot - Main Bot File
Combines functionality for anime info fetching and multporn image downloading
"""

import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from dotenv import load_dotenv

# Import utilities
from utils.anime_utils import fetch_anime_info
from utils.multporn_utils import scrape_images, download_image
from utils.pdf_utils import create_pdf_from_images
from utils.link_splitter import process_split_links

# Load environment variables
load_dotenv()
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Allowed Users
ALLOWED_USERS = {"1557539460", "6667553516", "5725206423", "6183939103"}

# Create the bot
bot = Client("anime_multporn_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# User session storage
USER_SELECTION = {}

# ========== BOT COMMANDS ==========
@bot.on_message(filters.command("start"))
async def start(client, message):
    """Handles the /start command."""
    if str(message.from_user.id) not in ALLOWED_USERS:
        await message.reply_text("🚫 You are not authorized to use this bot.")
        return
        
    await message.reply_text(
        "Welcome! This bot has multiple features:\n\n"
        "1. Use /anime to search for anime info\n"
        "2. Send a multporn.net link to download images and create PDF\n"
        "3. Use /split to get episode links\n"
        "4. Use /setparams to set anime name template"
    )

@bot.on_message(filters.command("anime"))
async def anime(client, message):
    """Handles the /anime command."""
    user_id = str(message.from_user.id)
    if user_id not in ALLOWED_USERS:
        await message.reply_text("🚫 You are not authorized to use this bot.")
        return
        
    await message.reply_text("📩 Send me the anime name:")
    USER_SELECTION[message.chat.id] = {"anime_name": None, "quality": None, "format": None}

@bot.on_message(filters.command("setparams"))
async def set_params(client, message):
    """
    Sets the anime name parameter.
    Usage: /setparams <anime_name with {episode}>
    """
    if str(message.from_user.id) not in ALLOWED_USERS:
        await message.reply_text("🚫 You are not authorized to use this command.")
        return
        
    try:
        _, args = message.text.split(" ", 1)
        USER_SELECTION[message.chat.id] = USER_SELECTION.get(message.chat.id, {})
        USER_SELECTION[message.chat.id]['anime_name'] = args.strip()
        await message.reply_text(f"✅ Anime name set to: {args.strip()}")
    except ValueError:
        await message.reply_text("❌ Invalid usage. Use /setparams <anime_name with {episode}>")

@bot.on_message(filters.command("split"))
async def split(client, message):
    """Initiates the link splitting process."""
    if str(message.from_user.id) not in ALLOWED_USERS:
        await message.reply_text("🚫 You are not authorized to use this command.")
        return
        
    USER_SELECTION[message.chat.id] = USER_SELECTION.get(message.chat.id, {})
    USER_SELECTION[message.chat.id]['state'] = 'split_start'
    await message.reply_text("Send start link")

@bot.on_message(filters.text & filters.private)
async def handle_text(client, message):
    """Handles text messages in private chats."""
    chat_id = message.chat.id
    user_id = str(message.from_user.id)
    
    if user_id not in ALLOWED_USERS:
        await message.reply_text("🚫 You are not authorized to use this bot.")
        return

    text = message.text.strip()

    # Handle Link Splitting feature
    if chat_id in USER_SELECTION and USER_SELECTION[chat_id].get("state") in ["split_start", "split_end"]:
        await handle_split_feature(client, message, chat_id, text)
        return

    # Handle Multporn URL
    if text.startswith("https://multporn.net/"):
        await handle_multporn_url(client, message, chat_id, text)
        return
        
    # Handle MultPorn image limit input
    if chat_id in USER_SELECTION and USER_SELECTION[chat_id].get("url") and "image_limit" not in USER_SELECTION[chat_id]:
        await handle_multporn_limit(client, message, chat_id, text)
        return
        
    # Handle Anime name input for /anime command
    if chat_id in USER_SELECTION and USER_SELECTION[chat_id].get("anime_name") is None:
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

async def handle_split_feature(client, message, chat_id, text):
    """Handle link splitting logic"""
    state = USER_SELECTION[chat_id]["state"]
    
    if state == "split_start":
        USER_SELECTION[chat_id]["start"] = text
        USER_SELECTION[chat_id]["state"] = "split_end"
        await message.reply_text("Now send end link")
        
    elif state == "split_end":
        start_link = USER_SELECTION[chat_id].get("start")
        end_link = text
        anime_name = USER_SELECTION[chat_id].get("anime_name", "")
        
        links = process_split_links(start_link, end_link, anime_name)
        
        if links:
            for i in range(0, len(links), 30):
                await message.reply_text(''.join(links[i:i + 30]))
        else:
            await message.reply_text("❌ Invalid links")
            
        USER_SELECTION[chat_id]['state'] = None

async def handle_multporn_url(client, message, chat_id, text):
    """Handle multporn url input"""
    import tempfile
    import shutil
    
    folder = os.path.join(tempfile.gettempdir(), f"downloads_{chat_id}")
    if os.path.exists(folder):
        shutil.rmtree(folder)
        
    USER_SELECTION[chat_id] = {"url": text, "folder": folder}
    await message.reply_text("How many images would you like to download?")

async def handle_multporn_limit(client, message, chat_id, text):
    """Handle multporn image limit input"""
    import tempfile
    
    try:
        limit = int(text)
        if limit < 1:
            raise ValueError
    except ValueError:
        await message.reply_text("❌ Please send a valid number.")
        return

    url = USER_SELECTION[chat_id]["url"]
    folder = USER_SELECTION[chat_id]["folder"]
    
    await message.reply_text("Fetching images, please wait...")
    
    # Create download folder
    os.makedirs(folder, exist_ok=True)
    
    # Scrape images
    image_urls, error = scrape_images(url)
    if error:
        await message.reply_text(f"Error: {error}")
        return

    selected_images = image_urls[:limit]
    if not selected_images:
        await message.reply_text("❌ No images found.")
        return
        
    USER_SELECTION[chat_id]["image_limit"] = limit
    
    # Download images
    progress_msg = await message.reply_text(f"0/{len(selected_images)} images downloaded")
    
    for idx, img_url in enumerate(selected_images, start=1):
        img_path = download_image(img_url)
        if img_path:
            ext = os.path.splitext(img_path)[1]
            new_name = os.path.join(folder, f"{idx}{ext}")
            os.rename(img_path, new_name)
            
            # Update progress every 5 images or on the last image
            if idx % 5 == 0 or idx == len(selected_images):
                await progress_msg.edit_text(f"{idx}/{len(selected_images)} images downloaded")

    await message.reply_text(f"✅ {len(selected_images)} image(s) downloaded. Generating PDF...")

    pdf_path = os.path.join(folder, "output.pdf")
    create_pdf_from_images(folder, pdf_path)
    
    # Send PDF
    await client.send_document(chat_id, pdf_path, file_name="multporn_images.pdf")
    
    # Send individual images
    for idx in range(1, len(selected_images) + 1):
        for ext in [".jpg", ".jpeg", ".png"]:
            file_path = os.path.join(folder, f"{idx}{ext}")
            if os.path.exists(file_path):
                await client.send_document(chat_id, file_path)
                break

    await message.reply_text("All images and PDF have been uploaded!")
    USER_SELECTION.pop(chat_id)

@bot.on_callback_query()
async def button_callback(client, callback_query):
    """Handles button callbacks."""
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

    elif data in ["otaku", "hanime", "ongoing"]:
        await process_anime_format(client, callback_query, chat_id, data)

async def process_anime_format(client, callback_query, chat_id, format_type):
    """Process the anime format selection and generate response."""
    anime_name = USER_SELECTION[chat_id]["anime_name"]
    quality = USER_SELECTION[chat_id]["quality"] or "Unknown"
    
    # Fetch anime info from AniList
    anime = await fetch_anime_info(anime_name)

    if not anime:
        await callback_query.message.reply_text("❌ Anime not found.")
        return

    anime_id = anime["id"]
    image_url = f"https://img.anili.st/media/{anime_id}"
    title = anime["title"]["english"] or anime["title"]["romaji"]
    genres_text = ", ".join(anime["genres"])
    genre_tags = " ".join([f"#{g}" for g in anime["genres"]])

    # Generate message text based on format type
    if format_type == "hanime":
        message_text = f"<b>💦 {title}\n╭──────────────────────\n├ 📺 Episode : {anime['episodes'] or 'N/A'}\n├ 💾 Quality : {quality}\n├ 🎭 Genres: {genres_text}\n├ 🔊 Audio track : Sub\n├ #Censored\n├ #Recommendation +++++++\n╰──────────────────────</b>"
    elif format_type == "otaku":
        message_text = f"""<b>💙 {title}</b>

<b>🎭 Genres :</b> {genres_text}
<b>🔊 Audio :</b> Dual Audio
<b>📡 Status :</b> Completed
<b>🗓 Episodes :</b> {anime['episodes'] or 'N/A'}
<b>💾 Quality :</b> {quality}
<b>✂️ Sizes :</b> 50MB, 120MB & 300MB
<b>🔞 Rating :</b> PG-13

<blockquote>📌 : {genre_tags}</blockquote>"""
    else:  # ongoing
        message_text = f"""❤️  {title}
╭───────────────────
├ 📺 Episodes : {anime['episodes'] or 'N/A'}
├ 💾 Quality : {quality}
├ 🎭 Genres: {genres_text}
├ 🔊 Audio track : Dual [English+Japanese]
╰───────────────────
Report Missing Episodes: @Otaku_Library_Support_Bot"""

    # Send the response
    await callback_query.message.reply_photo(
        photo=image_url,
        caption=message_text,
        parse_mode=ParseMode.HTML
    )
    
    # Clear user selection
    USER_SELECTION.pop(chat_id, None)

def main():
    """Main function to run the bot."""
    print("✅ Bot is running...")
    bot.run()

if __name__ == "__main__":
    main()
