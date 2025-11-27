from pyrogram import Client, filters, enums
from pyrogram.types import ChatPermissions, Message
from utils import extract_user, admin_filter
from plugins.Tools.help_func.string_handling import extract_time

@Client.on_message(filters.command("mute") & admin_filter)
async def mute_user(client: Client, message: Message):
    
    user_id, user_first_name = await extract_user(client, message)

    if not user_id:
        await message.reply_text("I can't find a user. Reply to someone or provide their user ID/username.")
        return

    try:
        await message.chat.restrict_member(
            user_id=user_id,
            permissions=ChatPermissions()
        )
    except Exception as error:
        await message.reply_text(str(error))
    else:
        await message.reply_text(
            f"👍🏻 <a href='tg://user?id={user_id}'>{user_first_name}</a>"
            f" അവൻ്റെ വായാ അടച്ചിട്ടുണ്ട്! 🤐"
        )

@Client.on_message(filters.command("tmute") & admin_filter)
async def temp_mute_user(client: Client, message: Message):

    if len(message.command) < 3:
        await message.reply_text("<b>Usage:</b> /tmute [user_id/username] [time]\n<b>Example:</b> /tmute @user 10m")
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
        await message.chat.restrict_member(
            user_id=user_id,
            permissions=ChatPermissions(),
            until_date=until_date_val
        )
    except Exception as error:
        await message.reply_text(str(error))
    else:
        await message.reply_text(
            f"മിണ്ടാതെ ഇരി കഴുതേ! 😠\n"
            f"<a href='tg://user?id={user_id}'>{user_first_name}</a>"
            f" muted for {time_val}!"
        )