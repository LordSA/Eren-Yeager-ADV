import re
from os import environ
from pyrogram import filters
from dotenv import load_dotenv

load_dotenv("config.env")
id_pattern = re.compile(r'^-?\d+$')

def is_enabled(value, default):
    if value.lower() in ["true", "yes", "1", "enable", "y"]:
        return True
    elif value.lower() in ["false", "no", "0", "disable", "n"]:
        return False
    else:
        return default


# Bot information
SESSION = environ.get('SESSION', 'Media_search')
API_ID = int(environ.get('API_ID', 0))
API_HASH = environ.get('API_HASH', None)
BOT_TOKEN = environ.get('BOT_TOKEN', None)
PM2_BOT_NAME = environ.get("PM2_BOT_NAME", None)
# Bot settings
CACHE_TIME = int(environ.get('CACHE_TIME', 300))
CHPV = environ.get('CHPV', 'pic').lower() #pic or vid
USE_CAPTION_FILTER = is_enabled(environ.get('USE_CAPTION_FILTER', "False"), False)
PICS = (environ.get('PICS', 'https://telegra.ph/file/069618da52d3a9bb4d8b3.jpg https://telegra.ph/file/b13191e1fc00971d98c86.jpg https://telegra.ph/file/81ad488d6a2348ca50b8e.jpg https://telegra.ph/file/fe08fd13ba44be8d25095.jpg https://telegra.ph/file/b8819d6efabcf072b50db.jpg https://telegra.ph/file/0d7276910a9d72233e5b3.jpg https://telegra.ph/file/3d087b3acc3c45e022b19.jpg https://telegra.ph/file/fd3b166e18c24e398cff7.jpg https://telegra.ph/file/62a0cf76eb841834f3d36.jpg https://telegra.ph/file/8642e8704dae11e44e8bc.jpg https://telegra.ph/file/1dd1a78d0130079b55114.jpg https://telegra.ph/file/4becd8f9d7a21531f62bd.jpg https://telegra.ph/file/b67c3e4d77418a9e6aa22.jpg https://telegra.ph/file/938ee7f76c5c897732528.jpg https://telegra.ph/file/4e68427f5b4c6c89a2670.jpg https://telegra.ph/file/c277bdb945f4aa077d06c.jpg https://telegra.ph/file/d558d0d9b262fdea5bea1.jpg')).split()
VIDS = (environ.get('VIDS', 'https://telegra.ph/file/e8c741846796427aa93a9.mp4 https://telegra.ph/file/863fb39bcabdd69a2ccda.mp4 https://telegra.ph/file/8f05c8bfff79cb7021022.mp4 https://telegra.ph/file/cd4a07a5fad5fdcf3084b.mp4 https://telegra.ph/file/fa5cb5c8c733a53abb488.mp4 https://telegra.ph/file/1612024aa1162ec5c0d9b.mp4 https://telegra.ph/file/971846d6b195589355d06.mp4 https://telegra.ph/file/fa6055633e209edb9d8ea.mp4 https://telegra.ph/file/9c3b6ddc4ab35ddef50a3.mp4')).split()
# Admins, Channels & Users
ADMINS = [int(admin) for admin in environ.get('ADMINS', '').split()]
CHANNELS = [int(ch) if id_pattern.search(ch) else ch for ch in environ.get('CHANNELS', '0').split()]
auth_users = [int(user) if id_pattern.search(user) else user for user in environ.get('AUTH_USERS', '').split()]
AUTH_USERS = (auth_users + ADMINS) if auth_users else []
auth_channel = environ.get('AUTH_CHANNEL')
auth_grp = environ.get('AUTH_GROUP')
AUTH_CHANNEL = int(auth_channel) if auth_channel and id_pattern.search(auth_channel) else None
AUTH_GROUPS = [int(ch) for ch in auth_grp.split()] if auth_grp else None
# MongoDB information
DATABASE_URI = environ.get('DATABASE_URI', None)
DATABASE_NAME = environ.get('DATABASE_NAME', "Rajappan")
COLLECTION_NAME = environ.get('COLLECTION_NAME', 'Telegram_files')
# Others
LOG_CHANNEL = int(environ.get('LOG_CHANNEL', 0))
SUPPORT_CHAT = environ.get('SUPPORT_CHAT', 'mwpro11')
P_TTI_SHOW_OFF = is_enabled((environ.get('P_TTI_SHOW_OFF', "False")), False)
IMDB = is_enabled((environ.get('IMDB', "True")), True)
SINGLE_BUTTON = is_enabled((environ.get('SINGLE_BUTTON', "False")), False)
CUSTOM_FILE_CAPTION = environ.get("CUSTOM_FILE_CAPTION", None)
BATCH_FILE_CAPTION = environ.get("BATCH_FILE_CAPTION", CUSTOM_FILE_CAPTION)
IMDB_TEMPLATE = environ.get("IMDB_TEMPLATE", "<b>Query: {query}</b> \n‌IMDb Data:\n\n🏷 Title: <a href={url}>{title}</a>\n🎭 Genres: {genres}\n📆 Year: <a href={url}/releaseinfo>{year}</a>\n🌟 Rating: <a href={url}/ratings>{rating}</a> / 10")
LONG_IMDB_DESCRIPTION = is_enabled(environ.get("LONG_IMDB_DESCRIPTION", "False"), False)
SPELL_CHECK_REPLY = is_enabled(environ.get("SPELL_CHECK_REPLY", "True"), True)
MAX_LIST_ELM = environ.get("MAX_LIST_ELM", None)
INDEX_REQ_CHANNEL = int(environ.get('INDEX_REQ_CHANNEL', LOG_CHANNEL))
FILE_STORE_CHANNEL = [int(ch) for ch in (environ.get('FILE_STORE_CHANNEL', '')).split()]
MELCOW_NEW_USERS = is_enabled((environ.get('MELCOW_NEW_USERS', "True")), True)
PROTECT_CONTENT = is_enabled((environ.get('PROTECT_CONTENT', "False")), False)
PUBLIC_FILE_STORE = is_enabled((environ.get('PUBLIC_FILE_STORE', "True")), True)
VERSION = "5.2.7[Beta]"

#BITLY
BITLY_KEY = environ.get("BITLY_KEY", None)

#IMDB [no need to  change]
TMD_API_KEY = "914840c590bcdda83b2c00e76519a90a"
TMD_API_BASE = "https://api.themoviedb.org/3"
IMG_BASE_URL = "https://image.tmdb.org/t/p/w500"


LOG_STR = "Current Cusomized Configurations are:-\n"
LOG_STR += ("IMDB Results are enabled, Bot will be showing imdb details for you queries.\n" if IMDB else "IMBD Results are disabled.\n")
LOG_STR += ("P_TTI_SHOW_OFF found , Users will be redirected to send /start to Bot PM instead of sending file file directly\n" if P_TTI_SHOW_OFF else "P_TTI_SHOW_OFF is disabled files will be send in PM, instead of sending start.\n")
LOG_STR += ("SINGLE_BUTTON is Found, filename and files size will be shown in a single button instead of two separate buttons\n" if SINGLE_BUTTON else "SINGLE_BUTTON is disabled , filename and file_sixe will be shown as different buttons\n")
LOG_STR += (f"CUSTOM_FILE_CAPTION enabled with value {CUSTOM_FILE_CAPTION}, your files will be send along with this customized caption.\n" if CUSTOM_FILE_CAPTION else "No CUSTOM_FILE_CAPTION Found, Default captions of file will be used.\n")
LOG_STR += ("Long IMDB storyline enabled." if LONG_IMDB_DESCRIPTION else "LONG_IMDB_DESCRIPTION is disabled , Plot will be shorter.\n")
LOG_STR += ("Spell Check Mode Is Enabled, bot will be suggesting related movies if movie not found\n" if SPELL_CHECK_REPLY else "SPELL_CHECK_REPLY Mode disabled\n")
LOG_STR += (f"MAX_LIST_ELM Found, long list will be shortened to first {MAX_LIST_ELM} elements\n" if MAX_LIST_ELM else "Full List of casts and crew will be shown in imdb template, restrict them by adding a value to MAX_LIST_ELM\n")
LOG_STR += f"Your current IMDB template is {IMDB_TEMPLATE}"

contact_filter = filters.create(
    lambda _, __, message:
    (message.from_user and message.from_user.is_contact) or message.outgoing
)

DEFAULT_SETTINGS = {
    'button': True,
    'botpm': True,
    'file_secure': False,
    'imdb': True,  # Set your desired default here
    'spell_check': True,
    'welcome': True,
    'template': IMDB_TEMPLATE # A default template
}
