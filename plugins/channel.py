from pyrogram import Client, filters
from info import CHANNELS
from database.ia_filterdb import save_file

media_filter = filters.document | filters.video | filters.audio

@Client.on_message(media_filter)
async def media(bot, message):
    """Media Handler"""
    if message.chat.id not in CHANNELS:
        return
    
    print(f"DEBUG: [Channel] Received message {message.id} in chat {message.chat.id}")
    if message.chat.type == "channel":
        print(f"DEBUG: [Channel] This is a channel post.")
    
    for file_type in ("document", "video", "audio"):
        media_obj = getattr(message, file_type, None)
        if media_obj is not None:
            print(f"DEBUG: [Channel] Found {file_type}: {getattr(media_obj, 'file_name', 'No Name')}")
            break
    else:
        print(f"DEBUG: [Channel] No supported media found in message.")
        return

    media_obj.file_type = file_type
    media_obj.caption = message.caption
    
    try:
        saved, status = await save_file(media_obj)
        if saved:
            print(f"DEBUG: [Channel] Successfully saved {media_obj.file_name} to DB.")
        else:
            print(f"DEBUG: [Channel] Failed to save to DB. Status: {status} (Duplicate: 0, Validation: 2, Error: 3)")
    except Exception as e:
        print(f"DEBUG: [Channel] Error calling save_file: {str(e)}")
