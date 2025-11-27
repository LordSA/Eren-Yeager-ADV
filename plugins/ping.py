import time
import random
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# -- Constants -- #
ALIVE = "എന്തിനാടാ start ഉണ്ടാകുമ്പോൾ എന്നെ നേക്കി എൻ്റെ വായിൽ ഉള്ളത് കേൾക്കുന്നത്... എന്നാ പരിപാടിയാ..." 
HELP = "ദൈവമേ എന്നെ മാത്രം രക്ഷിക്കണേ...."
REPO = "നമ്മൾ നമ്മൾ പോലുമറിയാതെ അധോലോകം ആയി മാറിക്കഴിഞ്ഞിരിക്കുന്നു ഷാജിയേട്ടാ..."
REPO_URL = "https://github.com/LordSA/Eren-Yeager-ADV"
# -- Constants End -- #


@Client.on_message(filters.command('alive'))
async def check_alive(_, message):
    await message.reply_text(ALIVE)

@Client.on_message(filters.command('ping'))
async def ping(_, message):
    start_t = time.time()
    rm = await message.reply_text("...")
    end_t = time.time()
    time_taken_s = (end_t - start_t) * 1000
    await rm.edit(f"Pong!\n{time_taken_s:.3f} ms")


@Client.on_message(filters.command('repo'))
async def repo(_, message):
    buttons = [[
        InlineKeyboardButton('『 Repo 』',url=REPO_URL)
        ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await message.reply_text(
        text = REPO,
        reply_markup = reply_markup,
        disable_web_page_preview=True
        )
