import re
import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from info import BITLY_KEY

URL_PATTERN = re.compile(r'(https?://\S+)')

async def get_tinyurl(long_url, alias=None):
    api_url = f"http://tinyurl.com/api-create.php?url={long_url}"
    if alias:
        api_url += f"&alias={alias}"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as response:
            result = await response.text()
            if response.status == 200 and "http" in result:
                return result
            return None

async def get_bitly(long_url, alias=None):
    headers = {
        "Authorization": f"Bearer {BITLY_KEY}",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        payload = {"long_url": long_url}
        async with session.post("https://api-ssl.bitly.com/v4/shorten", json=payload, headers=headers) as response:
            if response.status not in [200, 201]:
                return None
            data = await response.json()
            short_link = data.get("link")
            
        if alias and short_link:
            bitlink_id = short_link.replace("https://", "").replace("http://", "")
            custom_bitlink = f"bit.ly/{alias}"
            
            custom_payload = {
                "bitlink_id": bitlink_id,
                "custom_bitlink": custom_bitlink
            }
            
            async with session.post("https://api-ssl.bitly.com/v4/custom_bitlinks", json=custom_payload, headers=headers) as resp:
                if resp.status in [200, 201]:
                    return f"https://{custom_bitlink}"
                else:
                    return f"{short_link} (Alias '{alias}' unavailable)"
                    
        return short_link

@Client.on_message(filters.command(["short", "shorten"]))
async def shortener_handler(client, message: Message):
    url = None
    alias = None
    
    if len(message.command) >= 2:
        url = message.command[1]
        if len(message.command) >= 3:
            alias = message.command[2]
    
    elif message.reply_to_message:
        original_text = message.reply_to_message.text or message.reply_to_message.caption or ""
        match = URL_PATTERN.search(original_text)
        if match:
            url = match.group(0)
        if len(message.command) >= 2:
            alias = message.command[1]

    if not url:
        return await message.reply_text("❌ **Usage:**\n`/short [Link]`\n`/short [Link] [CustomName]`")

    if not url.startswith(("http://", "https://")):
        url = "http://" + url

    status_msg = await message.reply_text("🔄 **Shortening...**")

    try:
        if BITLY_KEY:
            short_link = await get_bitly(url, alias)
            service = "Bit.ly"
        else:
            short_link = await get_tinyurl(url, alias)
            service = "TinyURL"

        if not short_link:
            return await status_msg.edit(f"❌ **Error:** Could not shorten link.\nNote: Custom alias `{alias}` might be taken.")

        text = (
            f"✅ **Link Shortened!** ({service})\n\n"
            f"🔹 **Original:** {url}\n"
            f"🔸 **Short:** `{short_link}`"
        )
        
        btn = InlineKeyboardMarkup([[InlineKeyboardButton("🔗 Open Link", url=short_link)]])

        await status_msg.edit(text, reply_markup=btn, disable_web_page_preview=True)

    except Exception as e:
        await status_msg.edit(f"❌ **Error:** `{str(e)}`")