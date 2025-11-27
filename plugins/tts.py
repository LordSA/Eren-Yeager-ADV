import traceback
from io import BytesIO
import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message
import re

VOICES = [
    "nova", "alloy", "ash", "coral", "echo",
    "fable", "onyx", "sage", "shimmer"
]

INDIAN_LANGUAGES = {
    "malayalam": "Malayalam",
    "hindi": "Hindi", 
    "tamil": "Tamil",
    "bengali": "Bengali",
    "telugu": "Telugu",
    "marathi": "Marathi",
    "gujarati": "Gujarati",
    "kannada": "Kannada",
    "punjabi": "Punjabi",
    "urdu": "Urdu",
    "english": "coral",  # Default English voice
}

# Language detection patterns using Unicode ranges
LANGUAGE_PATTERNS = {
    "malayalam": re.compile(r'[\u0d00-\u0d7f]'),  # Malayalam
    "hindi": re.compile(r'[\u0900-\u097f]'),      # Devanagari (Hindi)
    "tamil": re.compile(r'[\u0b80-\u0bff]'),      # Tamil
    "bengali": re.compile(r'[\u0980-\u09ff]'),    # Bengali
    "telugu": re.compile(r'[\u0c00-\u0c7f]'),     # Telugu
    "gujarati": re.compile(r'[\u0a80-\u0aff]'),   # Gujarati
    "kannada": re.compile(r'[\u0c80-\u0cff]'),    # Kannada
    "marathi": re.compile(r'[\u0900-\u097f]'),    # Devanagari (Marathi)
    "punjabi": re.compile(r'[\u0a00-\u0a7f]'),    # Gurmukhi (Punjabi)
    "urdu": re.compile(r'[\u0600-\u06ff]'),       # Arabic script (Urdu)
}

def detect_language(text: str) -> str:
    """Auto-detect language from text using Unicode ranges."""
    for lang, pattern in LANGUAGE_PATTERNS.items():
        if pattern.search(text):
            return lang
    return "english"  # Default to English

def get_voice(voice: str) -> str:
    """Get valid voice name, support both English voices and Indian languages."""
    if not voice:
        return "coral"
    
    v = voice.lower().strip()
    
    # Check if it's an Indian language
    if v in INDIAN_LANGUAGES:
        return INDIAN_LANGUAGES[v]
    
    # Check if it's an English voice
    if v in VOICES:
        return v
    
    # Default fallback
    return "coral"

async def fetch_tts_primary(text: str, voice: str) -> BytesIO:
    """Primary TTS using ttsmp3.com API."""
    payload = {
        "msg": text,
        "lang": voice,
        "speed": "1.00",
        "source": "ttsmp3"
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
        async with session.post("https://ttsmp3.com/makemp3_ai.php", data=payload, headers=headers, timeout=15) as resp:
            if resp.status != 200:
                raise Exception(f"HTTP {resp.status}")
            
            data = await resp.json()
            if data.get("Error") != 0 or not data.get("URL"):
                raise Exception(f"API Error: {data.get('Error', 'Unknown')}")
            
            # Download audio
            async with session.get(data["URL"], timeout=20) as audio_resp:
                if audio_resp.status != 200:
                    raise Exception(f"Download failed: {audio_resp.status}")
                
                audio_bytes = await audio_resp.read()
                if len(audio_bytes) == 0:
                    raise Exception("Empty audio file")
                
                audio = BytesIO(audio_bytes)
                audio.name = f"tts_{voice}.mp3"
                audio.seek(0)
                return audio

async def fetch_tts_fallback(text: str, lang_code: str) -> BytesIO:
    """Fallback TTS using Google Translate TTS."""
    # Google TTS language codes
    google_lang_codes = {
        "malayalam": "ml", "hindi": "hi", "tamil": "ta", "bengali": "bn",
        "telugu": "te", "marathi": "mr", "gujarati": "gu", "kannada": "kn",
        "punjabi": "pa", "urdu": "ur", "english": "en"
    }
    
    # Get proper language code
    for lang_name, code in google_lang_codes.items():
        if lang_name.lower() in lang_code.lower() or code == lang_code:
            lang_code = code
            break
    
    # Limit text for Google TTS
    if len(text) > 200:
        text = text[:200] + "..."
    
    # Google Translate TTS endpoint
    url = "https://translate.google.com/translate_tts"
    params = {
        'ie': 'UTF-8',
        'q': text,
        'tl': lang_code,
        'client': 'tw-ob'
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20)) as session:
        async with session.get(url, params=params, headers=headers) as resp:
            if resp.status != 200:
                raise Exception(f"Google TTS failed: HTTP {resp.status}")
            
            audio_bytes = await resp.read()
            if len(audio_bytes) < 100:
                raise Exception("Invalid audio response from Google TTS")
            
            audio = BytesIO(audio_bytes)
            audio.name = f"gtts_{lang_code}.mp3"
            audio.seek(0)
            return audio

async def fetch_tts_audio(text: str, voice: str = "coral", speed: str = "1.00") -> tuple:
    """
    Fetch TTS audio with fallback support for Indian languages.
    Returns (audio_file, method_used)
    """
    voice = get_voice(voice)
    
    # Ensure text is properly encoded and cleaned
    text = str(text).strip()
    if not text:
        raise Exception("Empty text provided")
    
    # Limit text length to avoid API issues
    if len(text) > 3000:
        text = text[:3000] + "..."
    
    # Try primary API first for English voices and some Indian languages
    if voice in VOICES or voice in ["Hindi", "Tamil", "Bengali"]:
        try:
            audio_file = await fetch_tts_primary(text, voice)
            return audio_file, "Primary TTS"
        except Exception as e:
            print(f"Primary TTS failed: {e}")

    try:
        lang_for_google = voice
        if voice == "Malayalam":
            lang_for_google = "malayalam"
        elif voice == "Hindi":
            lang_for_google = "hindi"
        elif voice == "Tamil":
            lang_for_google = "tamil"
        elif voice == "Bengali":
            lang_for_google = "bengali"
        elif voice == "Telugu":
            lang_for_google = "telugu"
        elif voice == "Marathi":
            lang_for_google = "marathi"
        elif voice == "Gujarati":
            lang_for_google = "gujarati"
        elif voice == "Kannada":
            lang_for_google = "kannada"
        elif voice == "Punjabi":
            lang_for_google = "punjabi"
        elif voice == "Urdu":
            lang_for_google = "urdu"
        else:
            lang_for_google = "english"
        
        audio_file = await fetch_tts_fallback(text, lang_for_google)
        return audio_file, "Google TTS"
    
    except Exception as e:
        raise Exception(f"Both TTS services failed: {e}")

@Client.on_message(filters.command("tts"))
async def text_to_speech(client: Client, message: Message):
    """
    Telegram bot handler for /tts command with Indian language support.
    """
    try:
        if not message.reply_to_message:
            return await message.reply_text(
                "❌ Please reply to a message containing text.\n"
                "Usage: Reply to a text message and use /tts\n"
                "Example: /tts malayalam, /tts hindi, /tts tamil"
            )
        
        text_to_convert = None
        if message.reply_to_message.text:
            text_to_convert = message.reply_to_message.text
        elif message.reply_to_message.caption:
            text_to_convert = message.reply_to_message.caption
        
        if not text_to_convert or not text_to_convert.strip():
            return await message.reply_text("❌ The replied message doesn't contain any text.")
        
        # Parse voice/language from command
        voice = "coral"  # default voice
        command_args = message.text.split()[1:] if len(message.text.split()) > 1 else []
        
        if command_args:
            voice = get_voice(command_args[0])
        else:
            detected_lang = detect_language(text_to_convert)
            if detected_lang != "english":
                voice = get_voice(detected_lang)
                print(f"Auto-detected language: {detected_lang}")
        
        lang_display = voice if voice in INDIAN_LANGUAGES.values() else f"voice: {voice}"
        m = await message.reply_text(
            f"🎙️ Converting text to speech using {lang_display}\n"
            f"Text length: {len(text_to_convert)} characters"
        )
        audio_file, method_used = await fetch_tts_audio(text_to_convert, voice)
        
        # Send audio file
        await message.reply_audio(
            audio_file,
            caption=f"🎵 TTS Audio ({lang_display}) - {method_used}",
            performer="TTS Bot",
            title=f"TTS - {lang_display}"
        )
        
        # Delete processing message
        await m.delete()
        
    except Exception as e:
        error_msg = str(e)
        try:
            await m.edit_text(f"❌ Error: {error_msg}")
        except:
            await message.reply_text(f"❌ Error: {error_msg}")
        
        # Log full error for debugging
        print(f"TTS Error: {error_msg}")
        print(traceback.format_exc())

@Client.on_message(filters.command("ttshelp"))
async def tts_help(client: Client, message: Message):
    """Show TTS help information with Indian language support."""
    help_text = """
🎙️ **Text-to-Speech Bot Help**

**Usage:**
• Reply to any text message and use `/tts`
• Specify language: `/tts malayalam`

**Indian Languages:** 🇮🇳
• malayalam - മലയാളം
• hindi - हिन्दी  
• tamil - தமிழ்
• bengali - বাংলা
• telugu - తెలుగు
• marathi - मराठी
• gujarati - ગુજરાતી
• kannada - ಕನ್ನಡ
• punjabi - ਪੰਜਾਬੀ
• urdu - اردو

**English Voices:**
• nova, alloy, ash, coral, echo
• fable, onyx, sage, shimmer

**Examples:**
• `/tts malayalam` - Convert to Malayalam
• `/tts hindi` - Convert to Hindi
• `/tts coral` - Use coral English voice
• `/tts` - Auto-detect language

**Features:**
• Auto language detection from text
• Supports 10+ Indian languages
• Maximum 3000 characters per message
    """
    await message.reply_text(help_text)
