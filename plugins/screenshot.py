import os
import random
import asyncio
import static_ffmpeg
static_ffmpeg.add_paths()

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto

@Client.on_message(filters.command(["ss", "screenshot"]))
async def screenshot_handler(client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to a video to take a screenshot.")
    
    media = message.reply_to_message.video or message.reply_to_message.document
    if not media or not (getattr(media, "mime_type", "") or "").startswith("video/"):
        return await message.reply_text("Not a valid video file.")

    buttons = [
        [
            InlineKeyboardButton("1", callback_data="ss_cnt#1"),
            InlineKeyboardButton("2", callback_data="ss_cnt#2"),
            InlineKeyboardButton("3", callback_data="ss_cnt#3"),
        ],
        [
            InlineKeyboardButton("4", callback_data="ss_cnt#4"),
            InlineKeyboardButton("5", callback_data="ss_cnt#5"),
            InlineKeyboardButton("6", callback_data="ss_cnt#6"),
        ]
    ]
    
    await message.reply_text(
        "Select number of screenshots:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_callback_query(filters.regex("^ss_cnt"), group=-1)
async def screenshot_callback(client, query: CallbackQuery):
    count = int(query.data.split("#")[1])
    message = query.message.reply_to_message
    
    if not message:
        return await query.answer("Original message not found.", show_alert=True)

    await query.message.edit("Downloading video...")
    
    file_path = None
    screenshots = []
    
    try:
        file_path = await client.download_media(message)
        
        media = message.video or message.document
        duration = getattr(media, "duration", 0)
        
        if duration == 0:
            duration = 10 

        await query.message.edit("Generating screenshots...")
        
        timestamps = []
        for _ in range(count):
            timestamps.append(random.randint(0, duration - 1) if duration > 1 else 0)
        timestamps.sort()

        for i, ts in enumerate(timestamps):
            out_img = f"ss_{query.id}_{i}.jpg"
            
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
            await query.message.edit("Failed to take screenshot.")
        else:
            await query.message.edit("Uploading...")
            
            if len(screenshots) == 1:
                await query.message.reply_photo(screenshots[0])
            else:
                album = [InputMediaPhoto(img) for img in screenshots]
                await query.message.reply_media_group(album)
            
            await query.message.delete()

    except Exception as e:
        await query.message.edit(f"Error: {str(e)}")

    finally:
        if 'file_path' in locals() and file_path and os.path.exists(file_path):
            os.remove(file_path)
        for img in screenshots:
            if os.path.exists(img):
                os.remove(img)