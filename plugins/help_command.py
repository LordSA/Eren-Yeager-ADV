from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import MessageNotModified

HELP_TXT = """
<b>📚 Eren Yeager Bot Help Menu</b>

Select a category below to see available commands and their usage.

<b>⚪️ Categories:</b>
• 🎬 <b>Media & Download:</b> Song, Video, and Search.
• 📂 <b>Auto Filter:</b> How to search for movies/files.
• 🔄 <b>Automation:</b> Auto-Forwarding.
• 🛠 <b>Admin Only:</b> Management commands.
"""

MEDIA_TXT = """
<b>🎬 Media & Downloader Commands</b>

<b>🎵 Music</b>
`/song [Name]` 
<i>Search and download MP3 songs with thumbnails.</i>
Example: `/song Believer`

<b>🎞 Video</b>
`/video [Name]`
<i>Search YouTube and download video in 360p, 720p, 1080p, or 4K.</i>
Example: `/video Avatar Trailer`

<b>🔞 X-Search (If installed)</b>
`/xsearch [Query]`
<i>Search and download from external sources.</i>
"""

FILTER_TXT = """
<b>📂 Auto Filter & Indexing</b>

<b>🔍 Searching</b>
Just type the name of a movie or series in the group or bot PM.
The bot will check the database and return file links.

<b>🪄 Spell Check</b>
If you make a typo (e.g., "Avngers"), the bot will suggest the correct name.

<b>📜 IMDb Details</b>
The bot automatically fetches Rating, Plot, and Poster from IMDb.
"""

AUTO_FW_TXT = """
<b>🔄 Auto Forwarder</b>
<i>Automatically forwards messages from Source to Destination.</i>

<b>➕ Add Connection</b>
`/autofw [Source_ID] [Dest_ID]`
<i>Connects two channels. Bot must be Admin in both.</i>

<b>➖ Remove Connection</b>
`/unfw [Source_ID]`
<i>Stops forwarding from a specific channel.</i>

<b>📋 List Connections</b>
`/listfw`
<i>Shows all active forwarding tasks.</i>
"""

ADMIN_TXT = """
<b>🛠 Admin Commands (Owner Only)</b>

<b>⚙️ System</b>
• `/restart` - Restart the bot server.
• `/update` - Update bot from Git repo.
• `/checkupdate` - Check for new commits.
• `/logs` - Get system log file.

<b>🔌 Plugin Manager</b>
• `/install [Link]` - Install external plugin via Gist.
• `/uninstall [Name]` - Delete a plugin.
• `/pupdate [Name]` - Update a specific plugin.
• `/plugins` - List installed plugins.

<b>📝 Settings</b>
• `/index` - Index files from a channel.
• `/set_template` - Change the IMDb caption style.
• `/broadcast` - Send message to all users.
"""
def get_main_buttons():
    return [
        [
            InlineKeyboardButton("🎬 Media & DL", callback_data="help_media"),
            InlineKeyboardButton("📂 Auto Filter", callback_data="help_filter")
        ],
        [
            InlineKeyboardButton("🔄 Automation", callback_data="help_autofw"),
            InlineKeyboardButton("🛠 Admin Cmds", callback_data="help_admin")
        ],
        [
            InlineKeyboardButton("❌ Close", callback_data="close_data")
        ]
    ]

BACK_BUTTON = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="help_back")]]

@Client.on_message(filters.command("help"))
async def help_command(client, message):
    await message.reply_text(
        text=HELP_TXT,
        reply_markup=InlineKeyboardMarkup(get_main_buttons()),
        disable_web_page_preview=True
    )

@Client.on_callback_query(filters.regex("^help_"))
async def help_callback_handler(client, query: CallbackQuery):
    data = query.data.split("_")[1]
    
    if data == "back":
        text = HELP_TXT
        buttons = get_main_buttons()
    elif data == "media":
        text = MEDIA_TXT
        buttons = BACK_BUTTON
    elif data == "filter":
        text = FILTER_TXT
        buttons = BACK_BUTTON
    elif data == "autofw":
        text = AUTO_FW_TXT
        buttons = BACK_BUTTON
    elif data == "admin":
        text = ADMIN_TXT
        buttons = BACK_BUTTON
    else:
        text = HELP_TXT
        buttons = get_main_buttons()

    try:
        await query.message.edit(
            text=text,
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True
        )
    except MessageNotModified:
        pass