from pyrogram import Client, filters
from pyrogram.types import Message

@Client.on_message(filters.command(["stickerid"]))
async def stickerid(bot, message: Message):    
    if message.reply_to_message and message.reply_to_message.sticker:
        await message.reply(
            f"**Sticker ID is** \n `{message.reply_to_message.sticker.file_id}` \n \n"
            f"**Unique ID is** \n `{message.reply_to_message.sticker.file_unique_id}`",
            quote=True
        )
    else:
        await message.reply("Oops !! Not a sticker file", quote=True)