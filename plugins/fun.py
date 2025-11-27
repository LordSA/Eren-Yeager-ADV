from pyrogram import Client, filters

def aesthetify(string):
    PRINTABLE_ASCII = range(0x21, 0x7f)
    for c in string:
        c_ord = ord(c)
        if c_ord in PRINTABLE_ASCII:
            c_ord += 0xFF00 - 0x20
        elif c_ord == ord(" "):
            c_ord = 0x3000
        yield chr(c_ord)


@Client.on_message(filters.command(["ask"]))
async def aesthetic(client, message):
    status_message = await message.reply_text("What the hell do you want??\nപേടിച്ചു പോയോ ഞാൻ വെറുതേ പറഞ്ഞത")
    
    if len(message.command) < 2:
        await status_message.edit("...but you didn't give me any text.")
        return

    text = " ".join(message.command[1:])
    text = "".join(aesthetify(text))
    
    if not text:
        await status_message.edit("Couldn't convert that text.")
        return
        
    await status_message.edit(text)

DART_E_MOJI = "🎯"

@Client.on_message(filters.command(["throw", "dart"]))
async def throw_dart(client, message):
    rep_mesg_id = message.id
    if message.reply_to_message:
        rep_mesg_id = message.reply_to_message.id
    await client.send_dice(
        chat_id=message.chat.id,
        emoji=DART_E_MOJI,
        disable_notification=True,
        reply_to_message_id=rep_mesg_id
    )

DICE_E_MOJI = "🎲"

@Client.on_message(filters.command(["roll", "dice"]))
async def roll_dice(client, message):
    rep_mesg_id = message.id
    if message.reply_to_message:
        rep_mesg_id = message.reply_to_message.id
    await client.send_dice(
        chat_id=message.chat.id,
        emoji=DICE_E_MOJI,
        disable_notification=True,
        reply_to_message_id=rep_mesg_id
    )

TRY_YOUR_LUCK = "🎰"

@Client.on_message(filters.command(["luck", "cownd"]))
async def luck_cownd(client, message):
    rep_mesg_id = message.id
    if message.reply_to_message:
        rep_mesg_id = message.reply_to_message.id
    await client.send_dice(
        chat_id=message.chat.id,
        emoji=TRY_YOUR_LUCK,
        disable_notification=True,
        reply_to_message_id=rep_mesg_id
    )

GOAL_E_MOJI = "⚽"

@Client.on_message(filters.command(["goal", "shoot"]))
async def shoot_goal(client, message):
    rep_mesg_id = message.id
    if message.reply_to_message:
        rep_mesg_id = message.reply_to_message.id
    await client.send_dice(
        chat_id=message.chat.id,
        emoji=GOAL_E_MOJI,
        disable_notification=True,
        reply_to_message_id=rep_mesg_id
    )