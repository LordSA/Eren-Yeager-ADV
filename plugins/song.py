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
    user_info = f"User: {message.from_user.first_name} ({message.from_user.id})"
    logger.info(f"[COMMAND] /song triggered by {user_info}")
    
    if len(message.command) < 2:
        logger.warning(f"[COMMAND] Empty command query from {user_info}")
        return await message.reply_text("❌ **Usage:** `/song [Music Name or YT Link]`\n\nExample: `/song Believer`")

    query = message.text.split(None, 1)[1].strip()
    logger.info(f"[PROCESSING] Raw query received from {user_info}: '{query}'")
    m = await message.reply_text("🔎 **Processing...**")

    match = re.search(YT_URL_PATTERN, query)
    if match:
        vid_id = match.group(1)
        logger.info(f"[URL_MATCH] Direct YouTube link detected. Video ID extracted: {vid_id}")
        await m.delete()
        buttons = get_audio_quality_buttons(vid_id)
        logger.info(f"[UI] Sending quality selection panel directly for Video ID: {vid_id}")
        return await message.reply_text(
            f"🎧 **Select Audio Quality:**\nhttps://youtu.be/{vid_id}",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    try:
        logger.info(f"[SEARCH] Query '{query}' is a text search. Initializing yt-dlp search...")
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
            logger.warning(f"[SEARCH] No results returned for query: '{query}'")
            return await m.edit("❌ **No results found.**")

        search_id = str(uuid.uuid4())[:8]
        SEARCH_CACHE[search_id] = results
        logger.info(f"[CACHE] Stored {len(results)} search results under Search ID: {search_id}")

        await send_song_page(m, search_id, 0, query)

    except Exception as e:
        logger.error(f"[ERROR] Exception raised in song_search_handler: {e}", exc_info=True)
        await m.edit(f"❌ **Search Error:** `{str(e)}`")


async def send_song_page(message_object, search_id, offset, query_text):
    logger.info(f"[PAGE_RENDER] Fetching page for Search ID: {search_id} at offset: {offset}")
    results = SEARCH_CACHE.get(search_id)
    if not results:
        logger.warning(f"[CACHE_EXPIRED] Active session not found for Search ID: {search_id}")
        return await message_object.edit("❌ **Session expired.** Please search again.")

    current_batch = results[offset : offset + 5]
    logger.info(f"[PAGE_RENDER] Preparing batch of {len(current_batch)} tracks for inline layout display")
    
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
    logger.info(f"[UI_UPDATED] Search page updated successfully for Search ID: {search_id}")


@Client.on_callback_query(filters.regex("^spage"), group=-1)
async def song_page_callback(client, query):
    logger.info(f"[CALLBACK] Pagination pattern matched: '{query.data}' from User: {query.from_user.id}")
    try:
        _, search_id, offset_str = query.data.split("#")
        offset = int(offset_str)
        
        try:
            search_text = query.message.text.split("\n")[1].replace("Search: ", "")
        except Exception:
            search_text = "Results"
        
        await send_song_page(query.message, search_id, offset, search_text)
        await query.answer()
    except Exception as e:
        logger.error(f"[ERROR] Exception caught in song_page_callback: {e}", exc_info=True)


@Client.on_callback_query(filters.regex("^select_qual"), group=-1)
async def select_quality_callback(client, query):
    vid_id = query.data.split("#")[1]
    logger.info(f"[CALLBACK] Track selected. Fetching audio quality options for Video ID: {vid_id} (User: {query.from_user.id})")
    
    buttons = get_audio_quality_buttons(vid_id)
    await query.message.edit(
        f"🎧 **Select Audio Quality:**\nhttps://youtu.be/{vid_id}",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    await query.answer()
    logger.info(f"[UI_UPDATED] Resolution/Bitrate choices rendered to interface for Video ID: {vid_id}")


@Client.on_callback_query(filters.regex("^aud_dl"), group=-1)
async def download_song_callback(client: Client, query: CallbackQuery):
    _, vid_id, bitrate = query.data.split("#")
    link = f"https://www.youtube.com/watch?v={vid_id}"
    user_id = query.from_user.id
    
    logger.info(f"[CALLBACK] Download execution requested for Video ID: {vid_id} at {bitrate}kbps by User: {user_id}")
    await query.answer(f"📥 Initializing {bitrate}kbps Download...", show_alert=False)
    status_msg = await query.message.edit(f"📥 **Downloading {bitrate}kbps...**\n\n`{link}`")
    
    if not os.path.isdir(DOWNLOAD_LOCATION):
        os.makedirs(DOWNLOAD_LOCATION)
        logger.info(f"[FS] Created target local downloads directory tree at '{DOWNLOAD_LOCATION}'")
        
    unique_id = uuid.uuid4().hex[:6]
    output_path = f"{DOWNLOAD_LOCATION}/{vid_id}_{unique_id}.%(ext)s"
    file_path = f"{DOWNLOAD_LOCATION}/{vid_id}_{unique_id}.mp3"
    thumb_path = f"{DOWNLOAD_LOCATION}/{vid_id}_{unique_id}.jpg"

    try:
        logger.info(f"[DOWNLOAD_START] Handing off download context to yt-dlp for target link: {link}")
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
        
        logger.info(f"[DOWNLOAD_SUCCESS] Extraction complete. Meta retrieved - Title: '{title}', Duration: {duration}s")
        
        if not os.path.exists(thumb_path):
            thumb_path = f"{DOWNLOAD_LOCATION}/{vid_id}_{unique_id}.webp"
        if not os.path.exists(thumb_path):
            thumb_path = None
            logger.info("[FS] No valid media thumbnail file detected. Proceeding without target cover art.")
        else:
            logger.info(f"[FS] Visual artwork asset detected at: '{thumb_path}'")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Expected compiled MP3 binary file was not generated at path location: {file_path}")

        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        logger.info(f"[FS] Compiled file size verified: {file_size_mb:.2f} MB")

        logger.info(f"[UPLOAD] Despatching file structure payload downstream to Telegram Servers for Chat Context ID: {query.message.chat.id}")
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
        logger.info(f"[SUCCESS] Downstream delivery confirmed. File dispatched to client destination context successfully.")

    except Exception as e:
        logger.error(f"[ERROR] Exception caught inside core runtime pipeline of download_song_callback: {e}", exc_info=True)
        try:
            await status_msg.edit(f"❌ **Download Failed:**\n`{str(e)}`")
        except Exception:
            pass
    
    finally:
        logger.info("[CLEANUP] Initializing internal cleanup cycle protocols for temporary files storage context.")
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"[CLEANUP] Local temporary disk layout file erased successfully: '{file_path}'")
        if thumb_path and os.path.exists(thumb_path):
            os.remove(thumb_path)
            logger.info(f"[CLEANUP] Local temporary thumbnail artwork file erased successfully: '{thumb_path}'")


@Client.on_callback_query(filters.regex("^close_data"))
async def close_callback(client, query):
    logger.info(f"[CALLBACK] Window closing initialization requested by User: {query.from_user.id}")
    await query.message.delete()
    logger.info("[UI] Panel runtime configuration container view removed from target interface matrix hierarchy successfully.")