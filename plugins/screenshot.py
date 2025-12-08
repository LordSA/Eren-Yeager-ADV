import os
import random
import asyncio
import logging
import static_ffmpeg
from aiohttp import web
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto

static_ffmpeg.add_paths()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

STREAM_PORT = 8090

@Client.on_message(filters.command(["ss", "screenshot"]))
async def screenshot_handler(client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to a video.")
    
    media = message.reply_to_message.video or message.reply_to_message.document
    if not media or not (getattr(media, "mime_type", "") or "").startswith("video/"):
        return await message.reply_text("Not a valid video file.")

    video_id = message.reply_to_message.id

    buttons = [
        [
            InlineKeyboardButton("1", callback_data=f"ss_cnt#1#{video_id}"),
            InlineKeyboardButton("2", callback_data=f"ss_cnt#2#{video_id}"),
            InlineKeyboardButton("3", callback_data=f"ss_cnt#3#{video_id}"),
        ],
        [
            InlineKeyboardButton("5", callback_data=f"ss_cnt#5#{video_id}"),
            InlineKeyboardButton("8", callback_data=f"ss_cnt#8#{video_id}"),
            InlineKeyboardButton("10", callback_data=f"ss_cnt#10#{video_id}"),
        ]
    ]
    
    await message.reply_text(
        "⚡ **Fast Mode:** Select screenshot count:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_callback_query(filters.regex("^ss_cnt"), group=-1)
async def screenshot_callback(client, query: CallbackQuery):
    logger.info(f"[SS] Button clicked: {query.data}")
    
    try:
        parts = query.data.split("#")
        count = int(parts[1])
        video_msg_id = int(parts[2])
        chat_id = query.message.chat.id
        
        message = await client.get_messages(chat_id, video_msg_id)
        if not message or not (message.video or message.document):
            return await query.answer("Original video not found.", show_alert=True)

        media = message.video or message.document
        duration = getattr(media, "duration", 0)

        await query.message.edit("⚡ **Initializing Stream...**")

        async def media_stream_handler(request):
            try:
                range_header = request.headers.get("Range")
                file_size = media.file_size
                
                from_bytes, until_bytes = 0, file_size - 1
                if range_header:
                    from_bytes, until_bytes = range_header.replace("bytes=", "").split("-")
                    from_bytes = int(from_bytes)
                    until_bytes = int(until_bytes) if until_bytes else file_size - 1
                
                length = until_bytes - from_bytes + 1
                headers = {
                    "Content-Range": f"bytes {from_bytes}-{until_bytes}/{file_size}",
                    "Content-Length": str(length),
                    "Content-Type": "video/mp4",
                    "Accept-Ranges": "bytes",
                }
                
                response = web.StreamResponse(status=206 if range_header else 200, headers=headers)
                await response.prepare(request)
                
                chunk_size = 1024 * 1024
                offset = from_bytes // chunk_size
                
                async for chunk in client.stream_media(message, offset=offset):
                    if offset * chunk_size < from_bytes:
                        chunk = chunk[from_bytes - (offset * chunk_size):]
                    
                    try:
                        await response.write(chunk)
                    except:
                        break
                    offset += 1
                return response
            except Exception as e:
                logger.error(f"[SS] Stream Connection Error: {e}")
                return web.Response(status=500)
            finally:
                logger.info("[SS] Stream Connection Closed.")

        app = web.Application()
        app.router.add_get("/video.mp4", media_stream_handler)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "127.0.0.1", STREAM_PORT)
        await site.start()
        
        video_url = f"http://127.0.0.1:{STREAM_PORT}/video.mp4"
        logger.info(f"[SS] Streaming locally at {video_url}")

        if duration <= 10:
            await query.message.edit("⚡ **Probing Duration...**")
            try:
                cmd_probe = f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{video_url}"'
                proc_probe = await asyncio.create_subprocess_shell(
                    cmd_probe, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
                )
                stdout, _ = await proc_probe.communicate()
                duration = int(float(stdout.decode().strip()))
                logger.info(f"[SS] Probed Real Duration: {duration}s")
            except Exception as e:
                logger.warning(f"[SS] Probe failed: {e}. Defaulting to 10s.")
                duration = 10

        buffer = max(5, int(duration * 0.1)) 
        start_time = buffer
        end_time = duration - buffer
        
        if end_time <= start_time:
            timestamps = [duration // 2] * count
        else:
            timestamps = sorted([random.randint(start_time, end_time) for _ in range(count)])
        
        logger.info(f"[SS] Target Timestamps: {timestamps}")
        
        await query.message.edit(f"📸 **Extracting {count} Frames...**")
        
        screenshots = []
        for i, ts in enumerate(timestamps):
            out_img = f"ss_{query.id}_{i}.jpg"
            cmd = f'ffmpeg -ss {ts} -i "{video_url}" -frames:v 1 -q:v 2 "{out_img}" -y'
            
            proc = await asyncio.create_subprocess_shell(
                cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
            
            if os.path.exists(out_img):
                screenshots.append(out_img)

        await site.stop()
        await runner.cleanup()
        logger.info("[SS] Local Stream Server Stopped.")

        if not screenshots:
            await query.message.edit("Failed to extract frames (Stream Error).")
        else:
            await query.message.edit("📤 **Uploading...**")
            if len(screenshots) == 1:
                await query.message.reply_photo(screenshots[0], caption=f"📸 **Timestamp:** {timestamps[0]}s")
            else:
                album = [InputMediaPhoto(img) for img in screenshots]
                await query.message.reply_media_group(album, caption=f"📸 **{len(screenshots)} Screenshots**")
            
            await query.message.delete()
            logger.info(f"[SS] Successfully sent {len(screenshots)} screenshots to user.")

        for img in screenshots:
            if os.path.exists(img):
                os.remove(img)

    except Exception as e:
        logger.error(f"[SS] ERROR: {e}")
        await query.message.edit(f"Error: {str(e)}")