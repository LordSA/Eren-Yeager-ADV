# Made by Lord SA
import os
import re
import json
import base64
import random
import logging
import asyncio
import requests

from Script import script
from plugins.selector import MS
from pyrogram import Client, filters, enums
from pyrogram.errors import ChatAdminRequired, FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from database.ia_filterdb import Media, get_file_details
from database.users_chats_db import db
from info import CHANNELS, ADMINS, AUTH_CHANNEL, LOG_CHANNEL, BATCH_FILE_CAPTION, CUSTOM_FILE_CAPTION, PROTECT_CONTENT, CHPV, IMDB_TEMPLATE
from utils import get_settings, get_size, is_subscribed, save_group_settings, temp, FILE_ID_CACHE
from database.connections_mdb import active_connection
from plugins.Tools.help_func.decorators import check_group_admin

logger = logging.getLogger(__name__)
BATCH_FILES = {}

@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        buttons = [[
                InlineKeyboardButton('『𝕾𝚄𝙿𝙿𝙾𝚁𝚃』', url='https://t.me/mwpro11'),
                InlineKeyboardButton('『𝙷𝙴𝙻𝙿』', url=f"https://t.me/{temp.U_NAME}?start=help"),
            ],[   
                InlineKeyboardButton('➕ 𝕬𝙳𝙳 〽𝙴 𝕿𝙾 𝖄𝙾𝚄𝚁 𝕲𝚁𝙾𝚄𝙿 ➕', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
            ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply(script.START_TXT.format(message.from_user.mention if message.from_user else message.chat.title, temp.U_NAME, temp.B_NAME), reply_markup=reply_markup)
        await asyncio.sleep(2) 
        if not await db.get_chat(message.chat.id):
            total=await client.get_chat_members_count(message.chat.id)
            await client.send_message(LOG_CHANNEL, script.LOG_TEXT_G.format(message.chat.title, message.chat.id, total, "Unknown"))     
            await db.add_chat(message.chat.id, message.chat.title)
        return 
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(message.from_user.id, message.from_user.mention))
    if len(message.command) == 1:
        buttons = [[
            InlineKeyboardButton('➕ 𝕬𝙳𝙳 〽𝙴 𝕿𝙾 𝖄𝙾𝚄𝚁 𝕲𝚁𝙾𝚄𝙿 ➕', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
            ],[
            InlineKeyboardButton('『𝕾𝙴𝙰𝚁𝙲𝙷』', switch_inline_query_current_chat=''),
            InlineKeyboardButton('『𝕾𝚄𝙿𝙿𝙾𝚁𝚃』', url='https://t.me/mwpro11')
            ],[
            InlineKeyboardButton('『𝙲𝙷𝙰𝙽𝙽𝙴𝙻』', url='https://t.me/+2ZIFxHaOL8UzYjk1')
#           InlineKeyboardButton('『𝙶𝚁𝙾𝚄𝙿』', url='https://t.me/mwmoviespro')
            ],[
            InlineKeyboardButton('『𝙷𝙴𝙻𝙿』', callback_data='help'),
            InlineKeyboardButton('『𝕬𝙱𝙾𝚄𝚃』', callback_data='about')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        ct = script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME)
        if CHPV == 'vid':
            await message.reply_video(
                video=MS,
                caption=ct,
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )
        else:
            await message.reply_photo(
                photo=MS,
                caption=ct,
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )
        return
    data = message.command[1]

    if AUTH_CHANNEL and not await is_subscribed(client, message):
        logger.info(f"User {message.from_user.id} is not subscribed. Sending join link.")
        try:
            invite_link = await client.create_chat_invite_link(int(AUTH_CHANNEL))
        except ChatAdminRequired:
            logger.error("Make sure Bot is admin in Forcesub channel")
            return await message.reply("Bot is not admin in the updates channel. Cannot get link.")
        except Exception as e:
            logger.error(f"Error creating invite link: {e}")
            return await message.reply("Could not create invite link. Contact my admin.")
        btn = [
            [InlineKeyboardButton("『𝙹𝙾𝙸𝙽 𝙽𝙾𝚆』", url=invite_link.invite_link)],
            [InlineKeyboardButton("🔄 『𝚃𝚁𝚈 𝙰𝙶𝙰𝙸𝙽』", url=f"https://t.me/{temp.U_NAME}?start={data}")]
        ]
        await message.reply(
            text=script.JOIN_TXT,
            reply_markup=InlineKeyboardMarkup(btn),
            parse_mode=enums.ParseMode.MARKDOWN
        )
        return
    
    if data.startswith("auth_"):
        logger.info("User is subscribed, stripping 'auth_' prefix.")
        try:
           data = data.split("_", 2)[1] + "_" + data.split("_", 2)[2]
        except:
            logger.error(f"Error splitting auth_key: {data}")
            data = "help"
            
    if data in ["subscribe", "error", "okay", "help"]:
        buttons = [[
            InlineKeyboardButton('➕ 𝕬𝙳𝙳 〽𝙴 𝕿𝙾 𝖄𝙾𝚄𝚁 𝕲𝚁𝙾𝚄𝙿 ➕', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
            ],[
            InlineKeyboardButton('『𝕾𝙴𝙰𝚁𝙲𝙷』', switch_inline_query_current_chat=''),
            InlineKeyboardButton('『𝕾𝚄𝙿𝙿𝙾𝚁𝚃』', url='https://t.me/mwpro11')
            ],[
            InlineKeyboardButton('『𝙲𝙷𝙰𝙽𝙽𝙴𝙻』', url='https://t.me/+2ZIFxHaOL8UzYjk1')
#           InlineKeyboardButton('『𝙶𝚁𝙾𝚄𝙿』', url='https://t.me/')
            ],[
            InlineKeyboardButton('『𝙷𝙴𝙻𝙿』', callback_data='help'),
            InlineKeyboardButton('『𝕬𝙱𝙾𝚄𝚃』', callback_data='about')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        ct = script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME)
        if CHPV == 'vid':
            await message.reply_video(
                video=MS,
                caption=ct,
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )
        else:
            await message.reply_photo(
                photo=MS,
                caption=ct,
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )
        return
    if data.split("-", 1)[0] == "BATCH":
        sts = await message.reply("Please wait")
        file_id = data.split("-", 1)[1]
        msgs = BATCH_FILES.get(file_id)
        if not msgs:
            file = await client.download_media(file_id)
            try: 
                with open(file) as file_data:
                    msgs=json.loads(file_data.read())
            except:
                await sts.edit("FAILED")
                return await client.send_message(LOG_CHANNEL, "UNABLE TO OPEN FILE.")
            os.remove(file)
            BATCH_FILES[file_id] = msgs
        for msg in msgs:
            title = msg.get("title")
            size=get_size(int(msg.get("size", 0)))
            f_caption=msg.get("caption", "")
            if BATCH_FILE_CAPTION:
                try:
                    f_caption=BATCH_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
                except Exception as e:
                    logger.exception(e)
                    f_caption=f_caption
            if f_caption is None:
                f_caption = f"{title}"
            try:
                await client.send_cached_media(
                    chat_id=message.from_user.id,
                    file_id=msg.get("file_id"),
                    caption=f_caption,
                    protect_content=msg.get('protect', False),
                    )
            except FloodWait as e:
                await asyncio.sleep(e.x)
                logger.warning(f"Floodwait of {e.x} sec.")
                await client.send_cached_media(
                    chat_id=message.from_user.id,
                    file_id=msg.get("file_id"),
                    caption=f_caption,
                    protect_content=msg.get('protect', False),
                    )
            except Exception as e:
                logger.warning(e, exc_info=True)
                continue
            await asyncio.sleep(1) 
        await sts.delete()
        return
    elif data.split("-", 1)[0] == "DSTORE":
        sts = await message.reply("Please wait")
        b_string = data.split("-", 1)[1]
        decoded = (base64.urlsafe_b64decode(b_string + "=" * (-len(b_string) % 4))).decode("ascii")
        try:
            f_msg_id, l_msg_id, f_chat_id, protect = decoded.split("_", 3)
        except:
            f_msg_id, l_msg_id, f_chat_id = decoded.split("_", 2)
            protect = "/pbatch" if PROTECT_CONTENT else "batch"
        #diff = int(l_msg_id) - int(f_msg_id)
        msg_ids = list(range(int(f_msg_id), int(l_msg_id) + 1))
        try:
            messages = await client.get_messages(int(f_chat_id), msg_ids)
        except Exception as e:
            logger.error(f"Could Not Get Messages from DSTORE: {e}")
            return await sts.delete()
        for msg in messages:
            if msg.media:
                media = getattr(msg, msg.media.value)
                if BATCH_FILE_CAPTION:
                    try:
                        f_caption=BATCH_FILE_CAPTION.format(file_name=getattr(media, 'file_name', ''), file_size=getattr(media, 'file_size', ''), file_caption=getattr(msg, 'caption', ''))
                    except Exception as e:
                        logger.exception(e)
                        f_caption = getattr(msg, 'caption', '')
                else:
                    media = getattr(msg, msg.media.value)
                    file_name = getattr(media, 'file_name', '')
                    f_caption = getattr(msg, 'caption', file_name)
                try:
                    await msg.copy(message.chat.id, caption=f_caption, protect_content=True if protect == "/pbatch" else False)
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    await msg.copy(message.chat.id, caption=f_caption, protect_content=True if protect == "/pbatch" else False)
                except Exception as e:
                    logger.exception(e)
                    continue
            elif msg.empty:
                continue
            else:
                try:
                    await msg.copy(message.chat.id, protect_content=True if protect == "/pbatch" else False)
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    await msg.copy(message.chat.id, protect_content=True if protect == "/pbatch" else False)
                except Exception as e:
                    logger.exception(e)
                    continue
            await asyncio.sleep(1) 
        return await sts.delete()
        
    
    try:
        pre, key = data.split('_', 1)
    except:
        key = data
        pre = ""
    
    logger.info(f"User {message.from_user.id} requested file with key: {key}")
    file_id = FILE_ID_CACHE.get(key)

    if not file_id:
        logger.warning(f"File key {key} not found in cache. Link may be expired.") 
        try:
            pre, file_id = ((base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))).decode("ascii")).split("_", 1)
            logger.info("Legacy b64 file_id found.")
        except:
            logger.error(f"No valid file_id or cache key found for: {data}")
            return await message.reply('No such file exist.')
    try:
        files = await get_file_details(file_id)
        if not files:
            logger.error(f"File_id {file_id} not found in database.")
            return await message.reply('This file is no longer in my database.', quote=True)
    except Exception as e:
        logger.error(f"Error getting file details: {e}", exc_info=True)
        return await message.reply('An error occurred while fetching file details.', quote=True)
    file = files
    title = file.file_name
    size=get_size(file.file_size)
    f_caption=file.caption
    
    if CUSTOM_FILE_CAPTION:
        try:
            f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
        except Exception as e:
            logger.exception(e)
    
    if f_caption is None:
        f_caption = f"{file.file_name}"
    
    logger.info(f"Sending file {file_id} to user {message.from_user.id} in PM.")
    
    try:
        sent_message = await client.send_cached_media(
            chat_id=message.from_user.id,
            file_id=file_id,
            caption=f_caption,
            protect_content=True if pre == 'filep' else False,
        )
    except Exception as e:
        logger.error(f"Failed to send file {file_id} to {message.from_user.id}", exc_info=True)
        return await message.reply("I couldn't send the file. This might be because I can't start a PM with you (start me first!) or the file is corrupt.", quote=True)
    
    await asyncio.sleep(300) #timer for autodelete
    try:
        await sent_message.delete()
        logger.info(f"Auto-deleted message {sent_message.id} from PM.")
    except Exception as e:
        logger.warning(f"Could not auto-delete PM: {e}")

@Client.on_message(filters.command('channel') & filters.user(ADMINS))
async def channel_info(bot, message):
            
    """Send basic information of channel"""
    if isinstance(CHANNELS, (int, str)):
        channels = [CHANNELS]
    elif isinstance(CHANNELS, list):
        channels = CHANNELS
    else:
        raise ValueError("Unexpected type of CHANNELS")

    text = '📑 **Indexed channels/groups**\n'
    for channel in channels:
        chat = await bot.get_chat(channel)
        if chat.username:
            text += '\n@' + chat.username
        else:
            text += '\n' + chat.title or chat.first_name

    text += f'\n\n**Total:** {len(CHANNELS)}'

    if len(text) < 4096:
        await message.reply(text)
    else:
        file = 'Indexed channels.txt'
        with open(file, 'w') as f:
            f.write(text)
        await message.reply_document(file)
        os.remove(file)

LOG_FILE = "TelegramBot.log"

@Client.on_message(filters.command('logs') & filters.user(ADMINS))
async def log_file(client, message):
    
    if not os.path.exists(LOG_FILE):
        await message.reply_text("Log file not found. It might not have been created yet.")
        return
        
    if os.path.getsize(LOG_FILE) == 0:
        await message.reply_text("Log file is currently empty.")
        return

    try:
        await message.reply_document(LOG_FILE)
    except Exception as e:
        await message.reply_text(str(e))

@Client.on_message(filters.command('delete') & filters.user(ADMINS))
async def delete(bot, message):
    """Delete file from database"""
    reply = message.reply_to_message
    if reply and reply.media:
        msg = await message.reply("Processing...⏳", quote=True)
    else:
        await message.reply('Reply to file with /delete which you want to delete', quote=True)
        return

    for file_type in ("document", "video", "audio"):
        media = getattr(reply, file_type, None)
        if media is not None:
            break
    else:
        await msg.edit('This is not supported file format')
        return
    
    file_id = media.file_id

    result = await Media.collection.delete_one({
        '_id': file_id,
    })
    if result.deleted_count:
        await msg.edit('File is successfully deleted from database')
    else:
        file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
        result = await Media.collection.delete_many({
            'file_name': file_name,
            'file_size': media.file_size,
            'mime_type': media.mime_type
            })
        if result.deleted_count:
            await msg.edit('File is successfully deleted from database')
        else:
            result = await Media.collection.delete_many({
                'file_name': media.file_name,
                'file_size': media.file_size,
                'mime_type': media.mime_type
            })
            if result.deleted_count:
                await msg.edit('File is successfully deleted from database')
            else:
                await msg.edit('File not found in database')


@Client.on_message(filters.command('deleteall') & filters.user(ADMINS))
async def delete_all_index(bot, message):
    await message.reply_text(
        'This will delete all indexed files.\nDo you want to continue??',
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="YES", callback_data="autofilter_delete"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="CANCEL", callback_data="close_data"
                    )
                ],
            ]
        ),
        quote=True,
    )


@Client.on_callback_query(filters.regex(r'^autofilter_delete'))
async def delete_all_index_confirm(bot, message):
    await Media.collection.drop()
    await message.answer('Piracy Is Crime')
    await message.message.edit('Succesfully Deleted All The Indexed Files.')


@Client.on_message(filters.command('settings'))
@check_group_admin
async def settings(client, message, grp_id, title):
    settings = await get_settings(grp_id) 
    buttons = [
            [
                InlineKeyboardButton('『𝙵𝙸𝙻𝚃𝙴𝚁 𝙱𝚄𝚃𝚃𝙾𝙽』',
                                     callback_data=f'setgs#button#{settings.get("button", False)}#{str(grp_id)}'),
                InlineKeyboardButton('𝚂𝙸𝙽𝙶𝙻𝙴' if settings.get("button", False) else '𝙳𝙾𝚄𝙱𝙻𝙴',
                                     callback_data=f'setgs#button#{settings.get("button", False)}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('『𝙱𝙾𝚃 𝙿𝙼』', callback_data=f'setgs#botpm#{settings.get("botpm", False)}#{str(grp_id)}'),
                InlineKeyboardButton('✅ 𝚈𝙴𝚂' if settings.get("botpm", False) else '❌ 𝙽𝙾',
                                     callback_data=f'setgs#botpm#{settings.get("botpm", False)}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('『𝙵𝙸𝙻𝙴 𝚂𝙴𝙲𝚄𝚁𝙴』',
                                     callback_data=f'setgs#file_secure#{settings.get("file_secure", False)}#{str(grp_id)}'),
                InlineKeyboardButton('✅ 𝚈𝙴𝚂' if settings.get("file_secure", False) else '❌ 𝙽𝙾',
                                     callback_data=f'setgs#file_secure#{settings.get("file_secure", False)}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('『𝙸𝙼𝙳𝙱』', callback_data=f'setgs#imdb#{settings.get("imdb", False)}#{str(grp_id)}'),
                InlineKeyboardButton('✅ 𝚈𝙴𝚂' if settings.get("imdb", False) else '❌ 𝙽𝙾',
                                     callback_data=f'setgs#imdb#{settings.get("imdb", False)}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('『𝚂𝙿𝙴𝙻𝙻 𝙲𝙷𝙴𝙲𝙺』',
                                     callback_data=f'setgs#spell_check#{settings.get("spell_check", False)}#{str(grp_id)}'),
                InlineKeyboardButton('✅ 𝚈𝙴𝚂' if settings.get("spell_check", False) else '❌ 𝙽𝙾',
                                     callback_data=f'setgs#spell_check#{settings.get("spell_check", False)}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('『𝚆𝙴𝙻𝙲𝙾𝙼𝙴 𝚂𝙿𝙴𝙴𝙲𝙷』', callback_data=f'setgs#welcome#{settings.get("welcome", False)}#{str(grp_id)}'),
                InlineKeyboardButton('✅ 𝚈𝙴𝚂' if settings.get("welcome", False) else '❌ 𝙽𝙾',
                                     callback_data=f'setgs#welcome#{settings.get("welcome", False)}#{str(grp_id)}')
            ]
        ]

    reply_markup = InlineKeyboardMarkup(buttons)
    await message.reply_text(
        text=f"<b>Change Your Settings for {title} As Your Wish ⚙</b>",
        reply_markup=reply_markup,
        disable_web_page_preview=True,
        parse_mode=enums.ParseMode.HTML,
        reply_to_message_id=message.id
    )


@Client.on_message(filters.command('set_template'))
@check_group_admin
async def save_template(client, message, grp_id, title):
    sts = await message.reply("Checking template...")
    if len(message.command) < 2:
        return await sts.edit("❌ **Error:** Please provide a template text.\n\nUsage: `/set_template [your HTML template]`")
    template = message.text.split(" ", 1)[1]
    if template.lower().strip() == "default":
        await save_group_settings(grp_id, 'template', IMDB_TEMPLATE)
        return await sts.edit(f"Successfully **RESET** template for {title} to default!")
    await save_group_settings(grp_id, 'template', template)
    await sts.edit(f"Successfully changed template for {title} to:\n\n{template}")

@Client.on_message(filters.command('delete_template'))
@check_group_admin
async def delete_template_check(client, message, grp_id, title):
      sts = await message.reply("Restoring default template...")
      await save_group_settings(grp_id, 'template', IMDB_TEMPLATE)
      await sts.edit(f"✅ **Success!**\n\nThe template for **{title}** has been removed and reset to the bot's default.")