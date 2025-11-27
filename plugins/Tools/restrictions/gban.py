from pyrogram import Client, filters
from utils import extract_user, admin_filter
from plugins.Tools.help_func.string_handling import extract_time

@Client.on_message(filters.command("gban") & admin_filter)
async def ban_user(client, message):
    
    user_id, user_first_name = await extract_user(client, message)

    if not user_id:
        await message.reply_text("I can't find a user. Reply to someone or provide their user ID/username.")
        return

    try:
        await client.ban_chat_member(
            chat_id = message.chat.id,
            user_id=user_id
        )
    except Exception as error:
        await message.reply_text(
            str(error)
        )
    else:
        await message.reply_text(
            f"Someone else is dusting off..! "
            f"<a href='tg://user?id={user_id}'>"
            f"{user_first_name}"
            "</a>"
            " Is forbidden."
        )

@Client.on_message(filters.command("gtban") & admin_filter)
async def temp_ban_user(client, message):

    if len(message.command) < 3:
        await message.reply_text("<b>Usage:</b> /gtban [user_id/username] [time]\n<b>Example:</b> /gtban @user 10m")
        return

    user_id, user_first_name = await extract_user(client, message)

    if not user_id:
        await message.reply_text("I can't find a user. Reply to someone or provide their user ID/username.")
        return

    time_val = message.command[2]
    until_date_val = extract_time(time_val)
    
    if until_date_val is None:
        await message.reply_text(
            f"Invalid time type specified. Expected m, h, or d. Got: {time_val}"
        )
        return

    try:
        await client.ban_chat_member(
            chat_id=message.chat.id,
            user_id=user_id,
            until_date=until_date_val
        )
    except Exception as error:
        await message.reply_text(
            str(error)
        )
    else:
        await message.reply_text(
            f"Someone else is dusting off..! "
            f"<a href='tg://user?id={user_id}'>"
            f"{user_first_name}"
            "</a>"
            f" banned for {time_val}!"
        )