import os
import uuid
import asyncio
import logging
import yt_dlp
import static_ffmpeg
static_ffmpeg.add_paths()
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DOWNLOAD_LOCATION = "./downloads"
SEARCH_CACHE = {} 

@Client.on_message(filters.command(["song", "mp3", "music"]))
async def song_search_handler(client: Client, message: Message):
    logger.info(f"[SONG] Search command initiated by {message.from_user.first_name} ({message.from_user.id})")
    
    if len(message.command) < 2:
        return await message.reply_text("❌ **Usage:** `/song [Music Name]`\n\nExample: `/song Believer`")

    query = message.text.split(None, 1)[1]
    m = await message.reply_text("🔎 **Searching for song...**")
    logger.info(f"[SONG] Query: {query}")

    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'noplaylist': True,
            'extract_flat': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.info("[SONG] Running yt-dlp extraction...")
            info = await asyncio.to_thread(ydl.extract_info, f"ytsearch15:{query}", download=False)
            results = info.get('entries', [])
            logger.info(f"[SONG] Found {len(results)} results.")

        if not results:
            return await m.edit("❌ **No results found.**")

        search_id = str(uuid.uuid4())[:8]
        SEARCH_CACHE[search_id] = results
        logger.info(f"[SONG] Cache stored with ID: {search_id}")

        await send_song_page(m, search_id, 0, query)

    except Exception as e:
        logger.error(f"[SONG] Search Error: {e}")
        await m.edit(f"❌ **Search Error:** `{str(e)}`")


async def send_song_page(message_object, search_id, offset, query_text):
    logger.info(f"[SONG] Generating page. Offset: {offset}")
    results = SEARCH_CACHE.get(search_id)
    if not results:
        return await message_object.edit("❌ **Session expired.** Please search again.")

    current_batch = results[offset : offset + 5]
    
    buttons = []
    for video in current_batch:
        title = video.get('title')
        vid_id = video.get('id')
        duration = video.get('duration')
        
        if duration:
            mins, secs = divmod(duration, 60)
            time_str = f"{int(mins)}:{int(secs):02d}"
        else:
            time_str = "N/A"

        if len(title) > 30:
            title = title[:30] + "..."

        buttons.append([InlineKeyboardButton(f"🎵 {title} [{time_str}]", callback_data=f"dl_song#{vid_id}")])

    nav_btns = []
    if offset >= 5:
        nav_btns.append(InlineKeyboardButton("⬅️ Back", callback_data=f"spage#{search_id}#{offset - 5}"))
    
    if offset + 5 < len(results):
        nav_btns.append(InlineKeyboardButton("Next ➡️", callback_data=f"spage#{search_id}#{offset + 5}"))

    buttons.append(nav_btns)
    buttons.append([InlineKeyboardButton("❌ Close", callback_data="close_data")])

    text = f"🎧 **Select the song to download:**\nSearch: `{query_text}`\nShowing: {offset+1}-{min(offset+5, len(results))}"
    
    await message_object.edit(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^spage"), group=-1)
async def song_page_callback(client, query):
    logger.info(f"[SONG] Page navigation clicked: {query.data}")
    try:
        _, search_id, offset_str = query.data.split("#")
        offset = int(offset_str)
        
        try:
            search_text = query.message.text.split("\n")[1].replace("Search: ", "")
        except:
            search_text = "Results"
        
        await send_song_page(query.message, search_id, offset, search_text)
        await query.answer()
    except Exception as e:
        logger.error(f"[SONG] Page Nav Error: {e}")


@Client.on_callback_query(filters.regex("^dl_song"), group=-1)
async def download_song_callback(client: Client, query: CallbackQuery):
    logger.info(f"[SONG] Download button clicked. Data: {query.data}")
    
    await query.answer("📥 Initializing Download...", show_alert=False)
    
    try:
        vid_id = query.data.split("#")[1]
        link = f"https://www.youtube.com/watch?v={vid_id}"
        
        status_msg = await query.message.edit(f"📥 **Downloading...**\n\n`{link}`")
        logger.info(f"[SONG] Download started for: {link}")

        if not os.path.isdir(DOWNLOAD_LOCATION):
            os.makedirs(DOWNLOAD_LOCATION)
        
        output_path = f"{DOWNLOAD_LOCATION}/{vid_id}.%(ext)s"

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_path,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'writethumbnail': True,
            'quiet': True,
            'noplaylist': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = await asyncio.to_thread(ydl.extract_info, link, download=True)
            
        file_path = f"{DOWNLOAD_LOCATION}/{vid_id}.mp3"
        title = info_dict.get('title', 'Unknown Song')
        performer = info_dict.get('uploader', 'Unknown Artist')
        duration = info_dict.get('duration')
        
        thumb_path = f"{DOWNLOAD_LOCATION}/{vid_id}.jpg"
        if not os.path.exists(thumb_path):
            thumb_path = f"{DOWNLOAD_LOCATION}/{vid_id}.webp"
        if not os.path.exists(thumb_path):
            thumb_path = None

        logger.info("[SONG] Download complete. Uploading...")
        await status_msg.edit("📤 **Uploading...**")

        await client.send_audio(
            chat_id=query.message.chat.id,
            audio=file_path,
            title=title,
            performer=performer,
            duration=duration,
            thumb=thumb_path,
            caption=f"🎧 **{title}**\nUploaded by {client.me.mention}"
        )

        logger.info("[SONG] Upload complete.")
        await status_msg.delete()

    except Exception as e:
        logger.error(f"[SONG] Download/Upload Failed: {e}")
        try:
            await status_msg.edit(f"❌ **Download Failed:**\n`{str(e)}`")
        except:
            await query.message.edit(f"❌ **Error:** `{str(e)}`")
    
    finally:
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"[SONG] Deleted file: {file_path}")
        if 'thumb_path' in locals() and thumb_path and os.path.exists(thumb_path):
            os.remove(thumb_path)
            logger.info(f"[SONG] Deleted thumb: {thumb_path}")

@Client.on_callback_query(filters.regex("^close_data"))
async def close_callback(client, query):
    await query.message.delete()