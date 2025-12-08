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

    video_id = message.reply_to_message.id

    buttons = [
        [
            InlineKeyboardButton("1", callback_data=f"ss_cnt#1#{video_id}"),
            InlineKeyboardButton("2", callback_data=f"ss_cnt#2#{video_id}"),
            InlineKeyboardButton("3", callback_data=f"ss_cnt#3#{video_id}"),
        ],
        [
            InlineKeyboardButton("4", callback_data=f"ss_cnt#4#{video_id}"),
            InlineKeyboardButton("5", callback_data=f"ss_cnt#5#{video_id}"),
            InlineKeyboardButton("6", callback_data=f"ss_cnt#6#{video_id}"),
        ]
    ]
    
    await message.reply_text(
        "Select number of screenshots:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_callback_query(filters.regex("^ss_cnt"), group=-1)
async def screenshot_callback(client, query: CallbackQuery):
    try:
        parts = query.data.split("#")
        count = int(parts[1])
        video_msg_id = int(parts[2])
        
        chat_id = query.message.chat.id
        message = await client.get_messages(chat_id, video_msg_id)
        
        if not message or not (message.video or message.document):
            return await query.answer("Original video message deleted or not found.", show_alert=True)

        await query.message.edit("Downloading video header...")
        
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

        screenshots = []
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

        if 'file_path' in locals() and file_path and os.path.exists(file_path):
            os.remove(file_path)
        for img in screenshots:
            if os.path.exists(img):
                os.remove(img)

    except Exception as e:
        await query.message.edit(f"Error: {str(e)}")
        if 'file_path' in locals() and file_path and os.path.exists(file_path):
            os.remove(file_path)