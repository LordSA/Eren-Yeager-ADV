import re
import os
import uuid
import asyncio 
import logging
import requests


from cachetools import TTLCache
from pyrogram.errors import InputUserDeactivated, UserNotParticipant, FloodWait, UserIsBlocked, PeerIdInvalid
from info import AUTH_CHANNEL, LONG_IMDB_DESCRIPTION, MAX_LIST_ELM, TMD_API_KEY, TMD_API_BASE, IMG_BASE_URL, DEFAULT_SETTINGS ,ADMINS
from pyrogram.types import Message, InlineKeyboardButton, Audio, Document, Photo, Sticker, Video, VideoNote, Voice, Animation
from pyrogram import enums, filters
from typing import List, Union, Optional, Dict, Any
from database.users_chats_db import db
from bs4 import BeautifulSoup
from plugins.Tools.help_func.admin_check import admin_check


FILE_ID_CACHE = TTLCache(maxsize=1000, ttl=3600)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

BTN_URL_REGEX = re.compile(
    r"(\[([^\[]+?)\]\((buttonurl|buttonalert):(?:/{0,2})(.+?)(:same)?\))"
)

#imdb = IMDb()
AIO_SESSION = None
BANNED = {}
SMART_OPEN = '“'
SMART_CLOSE = '”'
START_CHAR = ('\'', '"', SMART_OPEN)


# temp db for banned 
class temp(object):
    BANNED_USERS = []
    BANNED_CHATS = []
    ME = None
    CURRENT=int(os.environ.get("SKIP", 2))
    CANCEL = False
    MELCOW = {}
    U_NAME = None
    B_NAME = None
    SETTINGS = {}

async def is_subscribed(bot, query):
    try:
        user = await bot.get_chat_member(AUTH_CHANNEL, query.from_user.id)
    except UserNotParticipant:
        pass
    except Exception as e:
        logger.exception(e)
    else:
        if user.status != 'kicked':
            return True

    return False

def list_to_str(k):
    if not k:
        return "N/A"
    elif len(k) == 1:
        return str(k[0])
    if MAX_LIST_ELM:
        k = k[:int(MAX_LIST_ELM)]
    return ', '.join(map(str, k))

def get_crew(crew_list: List[Dict[str, Any]], job: str) -> List[Dict[str, Any]]:
    """Helper to find crew members by their job title."""
    return [member for member in crew_list if member.get("job") == job]

async def get_poster(query: str, bulk: bool = False, id: bool = False, file: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
    if TMD_API_KEY == "BLAH BLAH":
        logger.error("TMDb API key is not set! 'get_poster' will not work.")
        return None

    try:
        if id:
            return await get_movie_details(query)
        else:
            return await search_movie(query, bulk)
    except Exception as e:
        logger.error(f"Error in get_poster (TMDb): {e}")
        return None

async def search_movie(query: str, bulk: bool = False) -> Optional[List[Dict[str, Any]]]:
    params = {'api_key': TMD_API_KEY, 'query': query}
    
    async with AIO_SESSION.get(f"{TMD_API_BASE}/search/movie", params=params) as response:
        if response.status != 200:
            logger.error(f"TMDb search API failed: {response.status}")
            return None
            
        data = await response.json()
        results = data.get("results")

        if not results:
            return None
        formatted_results = [
            {
                "movieID": movie.get("id"),
                "title": movie.get("title"),
                "year": movie.get("release_date", "N/A").split("-")[0]
            }
            for movie in results
        ]

        if bulk:
            return formatted_results
        else:
            first_movie_id = formatted_results[0].get("movieID")
            return await get_movie_details(first_movie_id)

async def get_movie_details(movie_id: str) -> Optional[Dict[str, Any]]:
    params = {'api_key': TMD_API_KEY, 'append_to_response': 'credits'}
    
    async with AIO_SESSION.get(f"{TMD_API_BASE}/movie/{movie_id}", params=params) as response:
        if response.status != 200:
            logger.error(f"TMDb details API failed: {response.status}")
            return None
            
        movie = await response.json()

    plot = movie.get('overview', 'N/A')
    if plot and LONG_IMDB_DESCRIPTION and len(plot) > 800:
        plot = plot[:800] + "..."
    elif not LONG_IMDB_DESCRIPTION and plot and len(plot) > 200:
         plot = plot[:200] + "..."
         
    poster_path = movie.get('poster_path')
    poster_url = f"{IMG_BASE_URL}{poster_path}" if poster_path else None
    cast = movie.get("credits", {}).get("cast", [])
    crew = movie.get("credits", {}).get("crew", [])
    return {
        'title': movie.get('title', 'N/A'),
        'votes': movie.get('vote_count', 'N/A'),
        "aka": movie.get("original_title", "N/A"),
        "seasons": "N/A",
        "box_office": f"${movie.get('revenue', 0):,}",
        'localized_title': movie.get('original_title', 'N/A'),
        'kind': "movie",
        "imdb_id": movie.get('imdb_id', f"tmdb{movie.get('id')}"),
        "cast": list_to_str([person.get('name') for person in cast]),
        "runtime": f"{movie.get('runtime', 0)} min",
        "countries": list_to_str([country.get('name') for country in movie.get("production_countries", [])]),
        "certificates": "N/A",
        "languages": list_to_str([lang.get('english_name') for lang in movie.get("spoken_languages", [])]),
        "director": list_to_str([person.get('name') for person in get_crew(crew, "Director")]),
        "writer": list_to_str([person.get('name') for person in get_crew(crew, "Writer")]),
        "producer": list_to_str([person.get('name') for person in get_crew(crew, "Producer")]),
        "composer": list_to_str([person.get('name') for person in get_crew(crew, "Original Music Composer")]) ,
        "cinematographer": list_to_str([person.get('name') for person in get_crew(crew, "Director of Photography")]),
        "music_team": list_to_str([person.get('name') for person in get_crew(crew, "Music")]),
        "distributors": list_to_str([company.get('name') for company in movie.get("production_companies", [])]),

        'release_date': movie.get('release_date', 'N/A'),
        'year': movie.get('release_date', 'N/A').split("-")[0],
        'genres': list_to_str([genre.get('name') for genre in movie.get("genres", [])]),
        'poster': poster_url,
        'plot': plot,
        'rating': f"{movie.get('vote_average', 0.0):.1f}",
        'url': movie.get('homepage') or f"https://www.themoviedb.org/movie/{movie_id}"
    }

async def broadcast_messages(user_id, message):
    try:
        await message.copy(chat_id=user_id)
        return True, "Success"
    except FloodWait as e:
        await asyncio.sleep(e.x)
        return await broadcast_messages(user_id, message)
    except InputUserDeactivated:
        await db.delete_user(int(user_id))
        logging.info(f"{user_id}-Removed from Database, since deleted account.")
        return False, "Deleted"
    except UserIsBlocked:
        logging.info(f"{user_id} -Blocked the bot.")
        return False, "Blocked"
    except PeerIdInvalid:
        await db.delete_user(int(user_id))
        logging.info(f"{user_id} - PeerIdInvalid")
        return False, "Error"
    except Exception as e:
        return False, "Error"

async def search_gagala(text):
    usr_agent = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/61.0.3163.100 Safari/537.36'
    }
    text = text.replace(" ", '+')
    url = f'https://www.google.com/search?q={text}'
    async with AIO_SESSION.get(url, headers=usr_agent) as response:
        response.raise_for_status()
        html = await response.text()
    soup = await asyncio.to_thread(BeautifulSoup, html, 'html.parser')
    titles = soup.find_all( 'h3' )
    return [title.getText() for title in titles]


async def get_settings(group_id):
    """
    This function is already perfect!
    It correctly uses the async db object.
    """
    try:
        group_id = int(group_id)
    except ValueError:
        logger.error(f"Invalid Group_id typr: {group_id}")
        return DEFAULT_SETTINGS.copy()
    
    settings = temp.SETTINGS.get(group_id)
    if settings is None:
        settings = DEFAULT_SETTINGS.copy()
        db_settings = await db.get_settings(group_id)
        if db_settings is not None:
            settings.update(db_settings)
        temp.SETTINGS[group_id] = settings
    return settings
    
async def save_group_settings(group_id, key, value):
    try:
        group_id = int(group_id)
    except ValueError:
        logger.error(f"Invalid group_id type for saving: {group_id}")
        return
    current = await get_settings(group_id)
    current[key] = value
    temp.SETTINGS[group_id] = current
    try:
        await db.update_settings(group_id, current)
    except Exception as e:
        logger.error(f"CRITICAL: FAILED TO SAVE SETTINGS TO DATABASE: {e}")
        
def get_size(size):
    """Get size in readable format"""

    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    size = float(size)
    i = 0
    while size >= 1024.0 and i < len(units):
        i += 1
        size /= 1024.0
    return "%.2f %s" % (size, units[i])

def split_list(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]   

MediaType = Union[
    "Audio", "Document", "Photo",
    "Sticker", "Video", "VideoNote",
    "Voice", "Animation"
]

def get_file_id(msg: Message) -> Optional[MediaType]:
    if not msg.media:
        return None 
    media_with_files = {
        enums.MessageMediaType.PHOTO,
        enums.MessageMediaType.ANIMATION,
        enums.MessageMediaType.AUDIO,
        enums.MessageMediaType.DOCUMENT,
        enums.MessageMediaType.VIDEO,
        enums.MessageMediaType.VIDEO_NOTE,
        enums.MessageMediaType.VOICE,
        enums.MessageMediaType.STICKER
    }

    if msg.media in media_with_files:
        return getattr(msg, msg.media.value)
    
    return None 

def extract_user(message: Message) -> Union[int, str]:
    """extracts the user from a message"""
    user_id = None
    user_first_name = None
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        user_first_name = message.reply_to_message.from_user.first_name

    elif len(message.command) > 1:
        if (
            len(message.entities) > 1 and
            message.entities[1].type == enums.MessageEntityType.TEXT_MENTION
        ):
            
            required_entity = message.entities[1]
            user_id = required_entity.user.id
            user_first_name = required_entity.user.first_name
        else:
            user_id = message.command[1]
            user_first_name = user_id
        try:
            user_id = int(user_id)
        except ValueError:
            pass
    else:
        user_id = message.from_user.id
        user_first_name = message.from_user.first_name
    return (user_id, user_first_name)


def last_online(from_user):
    time = ""
    if from_user.is_bot:
        time += "🤖 Bot :("
    elif from_user.status == enums.UserStatus.RECENTLY:
        time += "Recently"
    elif from_user.status == enums.UserStatus.LAST_WEEK:
        time += "Within the last week"
    elif from_user.status == enums.UserStatus.LAST_MONTH:
        time += "Within the last month"
    elif from_user.status == enums.UserStatus.LONG_AGO:
        time += "A long time ago :("
    elif from_user.status == enums.UserStatus.ONLINE:
        time += "Currently Online"
    elif from_user.status == enums.UserStatus.OFFLINE:
        time += from_user.last_online_date.strftime("%a, %d %b %Y, %H:%M:%S")
    return time


def split_quotes(text: str) -> List:
    if not any(text.startswith(char) for char in START_CHAR):
        return text.split(None, 1)
    counter = 1  # ignore first char -> is some kind of quote
    while counter < len(text):
        if text[counter] == "\\":
            counter += 1
        elif text[counter] == text[0] or (text[0] == SMART_OPEN and text[counter] == SMART_CLOSE):
            break
        counter += 1
    else:
        return text.split(None, 1)

    key = remove_escapes(text[1:counter].strip())
    rest = text[counter + 1:].strip()
    if not key:
        key = text[0] + text[0]
    return list(filter(None, [key, rest]))

def parser(text, keyword):
    if "buttonalert" in text:
        text = (text.replace("\n", "\\n").replace("\t", "\\t"))
    buttons = []
    note_data = ""
    prev = 0
    i = 0
    alerts = []
    for match in BTN_URL_REGEX.finditer(text):
        n_escapes = 0
        to_check = match.start(1) - 1
        while to_check > 0 and text[to_check] == "\\":
            n_escapes += 1
            to_check -= 1

        if n_escapes % 2 == 0:
            note_data += text[prev:match.start(1)]
            prev = match.end(1)
            if match.group(3) == "buttonalert":
                if bool(match.group(5)) and buttons:
                    buttons[-1].append(InlineKeyboardButton(
                        text=match.group(2),
                        callback_data=f"alertmessage:{i}:{keyword}"
                    ))
                else:
                    buttons.append([InlineKeyboardButton(
                        text=match.group(2),
                        callback_data=f"alertmessage:{i}:{keyword}"
                    )])
                i += 1
                alerts.append(match.group(4))
            elif bool(match.group(5)) and buttons:
                buttons[-1].append(InlineKeyboardButton(
                    text=match.group(2),
                    url=match.group(4).replace(" ", "")
                ))
            else:
                buttons.append([InlineKeyboardButton(
                    text=match.group(2),
                    url=match.group(4).replace(" ", "")
                )])

        else:
            note_data += text[prev:to_check]
            prev = match.start(1) - 1
    else:
        note_data += text[prev:]

    try:
        return note_data, buttons, alerts
    except:
        return note_data, buttons, None

def remove_escapes(text: str) -> str:
    res = ""
    is_escaped = False
    for counter in range(len(text)):
        if is_escaped:
            res += text[counter]
            is_escaped = False
        elif text[counter] == "\\":
            is_escaped = True
        else:
            res += text[counter]
    return res


def humanbytes(size):
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'

def f_owner_filter(filt, client, message):
    if not message or not message.from_user:
        return False
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    is_admin = user_id in ADMINS
    if is_admin:
        logger.debug(f"[OwnerFilter] ✅ Access GRANTED to {user_name} ({user_id})")
        return True
    else:
        logger.info(f"[OwnerFilter] ❌ Access DENIED to {user_name} ({user_id}). Not in ADMINS list.")
        return False

owner_filter = filters.create(
    func=f_owner_filter,
    name="OwnerFilter"
)

async def f_admin_filter(filt, client, message):
    if message.chat.type == enums.ChatType.PRIVATE:
        return False
    return await admin_check(message)

admin_filter = filters.create(
    func=f_admin_filter,
    name="AdminFilter"
)