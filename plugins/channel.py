from pyrogram import Client, filters, enums
from info import CHANNELS
from database.ia_filterdb import save_file

media_filter = filters.document | filters.video | filters.audio

@Client.on_message(filters.chat(CHANNELS) & media_filter, group=-1)
async def media(bot, message):
    """Media Handler"""
    # Debug to see if the ID filter is matching
    print(f"DEBUG: [Channel] Handler called for {message.id} in {message.chat.id}")
    
    # Check if it's a channel post or a group message
    if message.chat.type != enums.ChatType.CHANNEL:
        return
    
    # Check for media (redundant but safe)
    media_obj = None
    for file_type in ("document", "video", "audio"):
        media_obj = getattr(message, file_type, None)
        if media_obj is not None:
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
            # Status 0 usually means duplicate
            if status != 0:
                print(f"DEBUG: [Channel] Failed to save. Status: {status}")
    except Exception as e:
        print(f"DEBUG: [Channel] Error calling save_file: {str(e)}")
