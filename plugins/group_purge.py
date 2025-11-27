import asyncio
from datetime import datetime, timedelta
from pyrogram import Client, filters, enums
from pyrogram.errors import ChatAdminRequired, FloodWait
from plugins.group_tools import logger
from utils import admin_filter

@Client.on_message(filters.command("purge") & admin_filter)
async def purge(client, message):
    logger.info(f"Purge command triggered by user: {message.from_user.id}")
    if message.chat.type not in (enums.ChatType.SUPERGROUP, enums.ChatType.CHANNEL):
        await message.reply_text("This command only works in supergroups and channels.")
        return
    if not message.reply_to_message:
        await message.reply_text("Reply to a message to start purging from there.")
        return
    time_diff = datetime.now() - message.reply_to_message.date
    if time_diff > timedelta(hours=47): 
        await message.reply_text("⚠️ Cannot purge messages older than 48 hours due to Telegram limitations.")
        return
    try:
        chat_member = await client.get_chat_member(message.chat.id, "me")
        if not chat_member.privileges or not chat_member.privileges.can_delete_messages:
            await message.reply_text("I need 'Delete Messages' admin permission to use this command.")
            return
    except Exception as e:
        logger.error(f"Error checking bot permissions: {e}")
        await message.reply_text("Failed to verify permissions.")
        return
    try:
        status_message = await message.reply_text("🗑️ Processing purge...", quote=True)
        await message.delete()
    except ChatAdminRequired:
        await message.reply_text("I need to be an admin with 'Can delete messages' permission.")
        return
    except Exception as e:
        logger.error(f"Error on initial purge setup: {e}")
        return

    message_ids = []
    count_attempted = 0
    count_deleted = 0
    
    for message_id in range(
        message.reply_to_message.id,
        message.id + 1
    ):
        if message_id == status_message.id:
            continue
            
        message_ids.append(message_id)
        count_attempted += 1
        if len(message_ids) == 100:
            try:
                await client.delete_messages(
                    chat_id=message.chat.id,
                    message_ids=message_ids,
                    revoke=True
                )
                count_deleted += len(message_ids)
                logger.info(f"Deleted batch of {len(message_ids)} messages")
            except FloodWait as e:
                logger.warning(f"FloodWait of {e.value}s during purge")
                await asyncio.sleep(e.value)
                try:
                    await client.delete_messages(
                        chat_id=message.chat.id,
                        message_ids=message_ids,
                        revoke=True
                    )
                    count_deleted += len(message_ids)
                except Exception as retry_error:
                    logger.error(f"Error during retry after FloodWait: {retry_error}")
            except Exception as e:
                logger.error(f"Error during purge batch delete: {e}")
            
            message_ids = []
    if len(message_ids) > 0:
        try:
            await client.delete_messages(
                chat_id=message.chat.id,
                message_ids=message_ids,
                revoke=True
            )
            count_deleted += len(message_ids)
            logger.info(f"Deleted final batch of {len(message_ids)} messages")
        except FloodWait as e:
            logger.warning(f"FloodWait of {e.value}s during final purge")
            await asyncio.sleep(e.value)
            try:
                await client.delete_messages(
                    chat_id=message.chat.id,
                    message_ids=message_ids,
                    revoke=True
                )
                count_deleted += len(message_ids)
            except Exception as retry_error:
                logger.error(f"Error during retry after FloodWait: {retry_error}")
        except Exception as e:
            logger.error(f"Error during final purge delete: {e}")

    result_text = f"✅ Successfully purged {count_deleted} message(s)."
    if count_deleted < count_attempted:
        result_text += f"\n⚠️ {count_attempted - count_deleted} message(s) could not be deleted."
    
    await status_message.edit_text(result_text)
    await asyncio.sleep(5)
    try:
        await status_message.delete()
    except Exception as e:
        logger.error(f"Could not delete status message: {e}")

    logger.info(f"Purge completed: {count_deleted}/{count_attempted} messages deleted")