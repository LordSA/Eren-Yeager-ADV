import os
import math
import logging
import asyncio
import aiohttp
from aiohttp import web
from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from info import ADMINS

PORT = int(os.environ.get("PORT", 8080))
URL = os.environ.get("URL", os.environ.get("FQDN", None)) 

logger = logging.getLogger(__name__)
routes = web.RouteTableDef()

@routes.get("/")
async def root_handler(request):
    return web.Response(text="Stream Server is Running!")

@routes.get("/stream/{chat_id}/{message_id}")
async def stream_handler(request):
    try:
        chat_id = int(request.match_info["chat_id"])
        message_id = int(request.match_info["message_id"])
    except ValueError:
        return web.Response(status=400, text="Invalid ID")

    client = request.app["client"]

    try:
        msg = await client.get_messages(chat_id, message_id)
        media = msg.video or msg.document or msg.audio
        
        if not media:
            return web.Response(status=404, text="File not found")

        file_size = media.file_size
        file_name = media.file_name if hasattr(media, "file_name") else "video.mp4"
        mime_type = media.mime_type if hasattr(media, "mime_type") else "video/mp4"

        range_header = request.headers.get("Range")
        from_bytes, until_bytes = 0, file_size - 1
        
        if range_header:
            from_bytes, until_bytes = range_header.replace("bytes=", "").split("-")
            from_bytes = int(from_bytes)
            until_bytes = int(until_bytes) if until_bytes else file_size - 1

        length = until_bytes - from_bytes + 1
        
        headers = {
            "Content-Type": mime_type,
            "Content-Range": f"bytes {from_bytes}-{until_bytes}/{file_size}",
            "Content-Length": str(length),
            "Content-Disposition": f'inline; filename="{file_name}"',
            "Accept-Ranges": "bytes",
        }

        response = web.StreamResponse(status=206 if range_header else 200, headers=headers)
        await response.prepare(request)

        chunk_size = 1024 * 1024
        offset = from_bytes // chunk_size
        
        async for chunk in client.stream_media(msg, offset=offset):
            if offset * chunk_size < from_bytes:
                skip = from_bytes - (offset * chunk_size)
                chunk = chunk[skip:]
            
            try:
                await response.write(chunk)
            except Exception:
                break
            
            offset += 1

        return response

    except Exception as e:
        logger.error(f"Stream Error: {e}")
        return web.Response(status=500, text="Internal Server Error")


async def start_server(client):
    app = web.Application()
    app.add_routes(routes)
    app["client"] = client
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logger.info(f"🌐 Stream Server started on Port {PORT}")

@Client.on_message(filters.command("start_server") & filters.user(ADMINS))
async def manual_start(client, message):
    await start_server(client)
    await message.reply_text("✅ Server Started Manually.")

@Client.on_connect
async def on_startup_server(client):
    asyncio.create_task(start_server(client))

@Client.on_message(filters.command("stream"))
async def stream_command_handler(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("❌ **Reply to a video/file** with `/stream`.")

    media = message.reply_to_message.video or message.reply_to_message.document or message.reply_to_message.audio
    
    if not media:
        return await message.reply_text("❌ **Not a media file.**")

    msg = await message.reply_text("🔄 **Generating Link...**")

    global URL
    if not URL:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.ipify.org") as resp:
                    public_ip = await resp.text()
            URL = f"http://{public_ip}:{PORT}"
        except:
            return await msg.edit("❌ **Error:** Could not detect Public IP. Set `URL` variable in config.")

    stream_link = f"{URL.rstrip('/')}/stream/{message.reply_to_message.chat.id}/{message.reply_to_message.id}"

    text = f"🎥 **Stream Link Generated!**\n\n🔗 **Link:** `{stream_link}`\n\n⚠️ *Open this link in VLC or MX Player.*"
    
    await msg.edit(
        text,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("▶️ Watch Now", url=stream_link)]])
    )