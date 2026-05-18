import os
import uuid
import asyncio
import logging
import re
import yt_dlp
import static_ffmpeg
static_ffmpeg.add_paths()
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DOWNLOAD_LOCATION = "./downloads"
SEARCH_CACHE = {} 

YT_URL_PATTERN = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})"

def get_audio_quality_buttons(vid_id: str):
    return [
        [
            InlineKeyboardButton("🎵 128 kbps", callback_data=f"aud_dl#{vid_id}#128"),
            InlineKeyboardButton("🎵 192 kbps", callback_data=f"aud_dl#{vid_id}#192")
        ],
        [
            InlineKeyboardButton("🎵 256 kbps", callback_data=f"aud_dl#{vid_id}#256"),
            InlineKeyboardButton("🎵 320 kbps", callback_data=f"aud_dl#{vid_id}#320")
        ],
        [InlineKeyboardButton("❌ Close", callback_data="close_data")] 
    ]

@Client.on_message(filters.command(["song", "mp3", "music"]))
async def song_search_handler(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("❌ **Usage:** `/song [Music Name or YT Link]`\n\nExample: `/song Believer`")

    query = message.text.split(None, 1)[1].strip()
    m = await message.reply_text("🔎 **Processing...**")

    match = re.search(YT_URL_PATTERN, query)
    if match:
        vid_id = match.group(1)
        await m.delete()
        buttons = get_audio_quality_buttons(vid_id)
        return await message.reply_text(
            f"🎧 **Select Audio Quality:**\nhttps://youtu.be/{vid_id}",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'noplaylist': True,
            'extract_flat': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await asyncio.to_thread(ydl.extract_info, f"ytsearch15:{query}", download=False)
            results = info.get('entries', [])

        if not results:
            return await m.edit("❌ **No results found.**")

        search_id = str(uuid.uuid4())[:8]
        SEARCH_CACHE[search_id] = results

        await send_song_page(m, search_id, 0, query)

    except Exception as e:
        logger.error(f"[SONG] Search Error: {e}")
        await m.edit(f"❌ **Search Error:** `{str(e)}`")


async def send_song_page(message_object, search_id, offset, query_text):
    results = SEARCH_CACHE.get(search_id)
    if not results:
        return await message_object.edit("❌ **Session expired.** Please search again.")

    current_batch = results[offset : offset + 5]
    
    buttons = []
    for video in current_batch:
        title = video.get('title') or "No title"
        vid_id = video.get('id')
        duration = video.get('duration')
        
        if duration:
            mins, secs = divmod(duration, 60)
            time_str = f"{int(mins)}:{int(secs):02d}"
        else:
            time_str = "N/A"

        if len(title) > 30:
            title = title[:30] + "..."

        buttons.append([InlineKeyboardButton(f"🎵 {title} [{time_str}]", callback_data=f"select_qual#{vid_id}")])

    nav_btns = []
    if offset >= 5:
        nav_btns.append(InlineKeyboardButton("⬅️ Back", callback_data=f"spage#{search_id}#{offset - 5}"))
    
    if offset + 5 < len(results):
        nav_btns.append(InlineKeyboardButton("Next ➡️", callback_data=f"spage#{search_id}#{offset + 5}"))

    if nav_btns:
        buttons.append(nav_btns)
    buttons.append([InlineKeyboardButton("❌ Close", callback_data="close_data")])

    text = f"🎧 **Select the song to download:**\nSearch: `{query_text}`\nShowing: {offset+1}-{min(offset+5, len(results))}"
    
    await message_object.edit(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^spage"), group=-1)
async def song_page_callback(client, query):
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


@Client.on_callback_query(filters.regex("^select_qual"), group=-1)
async def select_quality_callback(client, query):
    vid_id = query.data.split("#")[1]
    buttons = get_audio_quality_buttons(vid_id)
    await query.message.edit(
        f"🎧 **Select Audio Quality:**\nhttps://youtu.be/{vid_id}",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    await query.answer()


@Client.on_callback_query(filters.regex("^aud_dl"), group=-1)
async def download_song_callback(client: Client, query: CallbackQuery):
    _, vid_id, bitrate = query.data.split("#")
    link = f"https://www.youtube.com/watch?v={vid_id}"
    
    await query.answer(f"📥 Initializing {bitrate}kbps Download...", show_alert=False)
    status_msg = await query.message.edit(f"📥 **Downloading {bitrate}kbps...**\n\n`{link}`")
    
    if not os.path.isdir(DOWNLOAD_LOCATION):
        os.makedirs(DOWNLOAD_LOCATION)
        
    unique_id = uuid.uuid4().hex[:6]
    output_path = f"{DOWNLOAD_LOCATION}/{vid_id}_{unique_id}.%(ext)s"
    file_path = f"{DOWNLOAD_LOCATION}/{vid_id}_{unique_id}.mp3"
    thumb_path = f"{DOWNLOAD_LOCATION}/{vid_id}_{unique_id}.jpg"

    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_path,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': bitrate,
            }],
            'writethumbnail': True,
            'quiet': True,
            'noplaylist': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = await asyncio.to_thread(ydl.extract_info, link, download=True)
            
        title = info_dict.get('title', 'Unknown Song')
        performer = info_dict.get('uploader', 'Unknown Artist')
        duration = info_dict.get('duration')
        
        if not os.path.exists(thumb_path):
            thumb_path = f"{DOWNLOAD_LOCATION}/{vid_id}_{unique_id}.webp"
        if not os.path.exists(thumb_path):
            thumb_path = None

        await status_msg.edit("📤 **Uploading...**")

        await client.send_audio(
            chat_id=query.message.chat.id,
            audio=file_path,
            title=title,
            performer=performer,
            duration=duration,
            thumb=thumb_path,
            caption=f"🎧 **{title}**\nQuality: {bitrate}kbps\nUploaded by {client.me.mention}"
        )

        await status_msg.delete()

    except Exception as e:
        logger.error(f"[SONG] Download/Upload Failed: {e}")
        try:
            await status_msg.edit(f"❌ **Download Failed:**\n`{str(e)}`")
        except:
            pass
    
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
        if thumb_path and os.path.exists(thumb_path):
            os.remove(thumb_path)


@Client.on_callback_query(filters.regex("^close_data"))
async def close_callback(client, query):
    await query.message.delete()