import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import ChatAdminRequired, RightForbidden
from utils import admin_filter

logger = logging.getLogger(__name__)
@Client.on_message(filters.command("pin") & admin_filter)
async def pin(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("Reply to a message to pin it.")
        return

    logger.info(f"User {message.from_user.id} attempting to pin message {message.reply_to_message.id} in chat {message.chat.id}")

    try:
        await message.reply_to_message.pin()
        await message.reply_text("Pinned the message!", quote=True)
        logger.info(f"Successfully pinned message {message.reply_to_message.id}.")
    except ChatAdminRequired:
        logger.warning(f"Failed to pin: Bot is not an admin in chat {message.chat.id}.")
        await message.reply_text("I'm not an admin here. I need admin rights to pin messages.")
    except RightForbidden:
        logger.warning(f"Failed to pin: Bot is missing 'Can pin messages' permission in chat {message.chat.id}.")
        await message.reply_text("I don't have the 'Can pin messages' permission.")
    except Exception as e:
        logger.error(f"Failed to pin message {message.reply_to_message.id}: {e}", exc_info=True)
        await message.reply_text(f"An error occurred: {e}")


@Client.on_message(filters.command("unpin") & admin_filter)
async def unpin(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("Reply to a message to unpin it.")
        return
        
    logger.info(f"User {message.from_user.id} attempting to unpin message {message.reply_to_message.id} in chat {message.chat.id}")

    try:
        await message.reply_to_message.unpin()
        await message.reply_text("Unpinned the message!", quote=True)
        logger.info(f"Successfully unpinned message {message.reply_to_message.id}.")
    except ChatAdminRequired:
        logger.warning(f"Failed to unpin: Bot is not an admin in chat {message.chat.id}.")
        await message.reply_text("I'm not an admin here. I need admin rights to unpin messages.")
    except RightForbidden:
        logger.warning(f"Failed to unpin: Bot is missing 'Can pin messages' permission in chat {message.chat.id}.")
        await message.reply_text("I don't have the 'Can pin messages' permission.")
    except Exception as e:
        logger.error(f"Failed to unpin message {message.reply_to_message.id}: {e}", exc_info=True)
        await message.reply_text(f"An error occurred: {e}")