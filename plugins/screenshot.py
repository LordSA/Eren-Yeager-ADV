import os
import time
import random
import asyncio
import static_ffmpeg
static_ffmpeg.add_paths()

from pyrogram import Client, filters
from pyrogram.types import Message, InputMediaPhoto

def get_seconds(time_string):
    """Converts MM:SS or HH:MM:SS to seconds"""
    try:
        parts = list(map(int, time_string.split(':')))
        if len(parts) == 1: return parts[0] # Seconds
        if len(parts) == 2: return parts[0]*60 + parts[1] # MM:SS
        if len(parts) == 3: return parts[0]*3600 + parts[1]*60 + parts[2] # HH:MM:SS
    except:
        return 0
    return 0

@Client.on_message(filters.command(["ss", "screenshot"]))
async def screenshot_handler(client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("❌ **Reply to a video** to take a screenshot.")
    
    media = message.reply_to_message.video or message.reply_to_message.document
    if not media or not media.mime_type.startswith("video/"):
        return await message.reply_text("❌ **Not a valid video file.**")

    sts = await message.reply_text("📥 **Downloading video header...**")
    

    cmd_args = message.command
    mode = "random"
    target_time = 0
    count = 1

    if len(cmd_args) > 1:
        arg = cmd_args[1]
        if ":" in arg:
            mode = "specific"
            target_time = get_seconds(arg)
        elif arg.isdigit():
            val = int(arg)
            if val < 10: 
                mode = "multi"
                count = val
            else: 
                mode = "specific"
                target_time = val

    try:
        file_path = await client.download_media(message.reply_to_message)
        await sts.edit("📸 **Generating Screenshot(s)...**")

        duration = getattr(media, "duration", 0)
        
        screenshots = []
        timestamps = []
        if mode == "specific":
            timestamps.append(target_time)
        elif mode == "random":
            timestamps.append(random.randint(0, duration - 1) if duration > 0 else 5)
        elif mode == "multi":
            step = duration // (count + 1)
            for i in range(1, count + 1):
                timestamps.append(i * step)
        for i, ts in enumerate(timestamps):
            out_img = f"ss_{message.id}_{i}.jpg"
            cmd = f'ffmpeg -ss {ts} -i "{file_path}" -frames:v 1 -q:v 2 "{out_img}" -y'
            
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
            
            if os.path.exists(out_img):
                screenshots.append(out_img)
        if not screenshots:
            await sts.edit("❌ **Failed to take screenshot.** (Video might be corrupt or 0s length)")
        else:
            await sts.edit("📤 **Uploading...**")
            
            if len(screenshots) == 1:
                await message.reply_photo(screenshots[0], caption=f"📸 **Screenshot at:** `{timestamps[0]}s`")
            else:
                album = [InputMediaPhoto(img) for img in screenshots]
                await message.reply_media_group(album, caption=f"📸 **{len(screenshots)} Screenshots generated.**")

    except Exception as e:
        await sts.edit(f"❌ **Error:** `{str(e)}`")

    finally:
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        for img in screenshots:
            if os.path.exists(img):
                os.remove(img)
        await sts.delete()