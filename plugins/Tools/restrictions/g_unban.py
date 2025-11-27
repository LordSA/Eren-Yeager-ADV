from pyrogram import Client, filters, enums
from pyrogram.types import Message
from utils import extract_user, admin_filter
@Client.on_message(filters.command("gunban") & admin_filter)
async def unban_user(client: Client, message: Message):
    
    user_id, user_first_name = await extract_user(client, message)

    if not user_id:
        await message.reply_text("I can't find a user. Reply to someone or provide their user ID/username.")
        return

    try:
        await message.chat.unban_member(
            user_id=user_id
        )
    except Exception as error:
        await message.reply_text(str(error))
    else:
        await message.reply_text(
            f"✅ **Unbanned!**\n\n"
            f"User: <a href='tg://user?id={user_id}'>{user_first_name}</a>\n"
            f"They can now rejoin the group."
        )

@Client.on_message(filters.command("unmute") & admin_filter)
async def unmute_user(client: Client, message: Message):
    
    user_id, user_first_name = await extract_user(client, message)
    
    if not user_id:
        await message.reply_text("I can't find a user. Reply to someone or provide their user ID/username.")
        return

    try:
        await message.chat.unban_member(
            user_id=user_id
        )
    except Exception as error:
        await message.reply_text(str(error))
    else:
        await message.reply_text(
            f"✅ **Unmuted!**\n\n"
            f"User: <a href='tg://user?id={user_id}'>{user_first_name}</a>\n"
            f"They can now speak in the group."
        )