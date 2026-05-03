from pyrogram import Client, filters
from info import CHANNELS
from database.ia_filterdb import save_file

media_filter = filters.document | filters.video | filters.audio

@Client.on_message(filters.chat(CHANNELS) & media_filter)
async def media(bot, message):
    """Media Handler"""
    for file_type in ("document", "video", "audio"):
        media_obj = getattr(message, file_type, None)
        if media_obj is not None:
            break
    else:
        return

    media_obj.file_type = file_type
    media_obj.caption = message.caption
    
    await save_file(media_obj)
