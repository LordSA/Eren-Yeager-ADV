import sys
import aiohttp
import logging
import logging.config
import subprocess
import asyncio 
from pyrogram import Client, __version__ 
#from pyrogram.types import Message
from info import SESSION, API_ID, API_HASH, BOT_TOKEN, LOG_STR

# Get logging configurations
logging.config.fileConfig('logging.conf')
logger = logging.getLogger(__name__)
logger.info("Bot is starting with logging configured from file...")

from pyrogram.raw.all import layer
from database.ia_filterdb import Media
from database.filters_mdb import filters_db
from database.users_chats_db import db
from utils import temp
import utils

class Bot(Client):

    def __init__(self):
        super().__init__(
            name=SESSION,
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=50,
            plugins={"root": "plugins"},
            sleep_threshold=5,
        )

    async def start(self):
        b_users, b_chats = await db.get_banned()
        temp.BANNED_USERS = b_users
        temp.BANNED_CHATS = b_chats
        await super().start()
        utils.AIO_SESSION = aiohttp.ClientSession()
        await Media.ensure_indexes()
        await filters_db.create_index()
        me = await self.get_me()
        temp.ME = me.id
        temp.U_NAME = me.username
        temp.B_NAME = me.first_name
        self.username = '@' + me.username
        logging.info(f"{me.first_name} with for Pyrogram v{__version__} (Layer {layer}) started on {me.username}.")
        logging.info(LOG_STR)

    async def stop(self, *args):
        if utils.AIO_SESSION:
            await utils.AIO_SESSION.close()
            
        await super().stop()
        logging.info("Bot stopped. Bye.")
    
app = Bot()
app.run()