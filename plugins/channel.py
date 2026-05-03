from pyrogram import Client, filters, enums
from info import CHANNELS
from database.ia_filterdb import save_file

media_filter = filters.document | filters.video | filters.audio

@Client.on_message(filters.chat(CHANNELS))
async def media(bot, message):
    """Media Handler"""
    # Debug to see if the ID filter is matching
    print(f"DEBUG: [Channel] Received update in {message.chat.id} from monitored list.")
    
    # Check if it's a channel post or a group message
    if message.chat.type != enums.ChatType.CHANNEL:
        return
    
    # Check for media
    media_obj = None
    for file_type in ("document", "video", "audio"):
        media_obj = getattr(message, file_type, None)
        if media_obj is not None:
            print(f"DEBUG: [Channel] Found {file_type}: {getattr(media_obj, 'file_name', 'No Name')}")
            break
    
    if not media_obj:
        return

    media_obj.file_type = file_type
    media_obj.caption = message.caption
    
    try:
        saved, status = await save_file(media_obj)
        if saved:
            print(f"DEBUG: [Channel] Successfully saved {media_obj.file_name} to DB.")
        else:
            print(f"DEBUG: [Channel] Failed to save. Status: {status}")
    except Exception as e:
        print(f"DEBUG: [Channel] Error calling save_file: {str(e)}")
