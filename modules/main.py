import os
import re
import sys
import json
import time
import asyncio
import requests
import subprocess

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from subprocess import getstatusoutput

from vars import api_id, api_hash, bot_token

bot = Client(
    "bot",
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token
)

# User-specific channels
user_channels = {}
active_users = set()

@bot.on_message(filters.command("start"))
async def start_message(bot: Client, m: Message):
    await m.reply_text(f"""
Hello, [{m.from_user.first_name}](tg://user?id={m.from_user.id}) 👋

Welcome to **Stylish Downloader Bot**!
This bot can download videos and PDFs from various sources.

Commands:
- `/setchannel` - Set the target channel to post files.
- `/showchannel` - Show your current target channel.
- `/crchoudhary` - Start downloading process.
- `/stop` - Stop the bot process for your session.

Enjoy the bot, and for updates join @targetallcourse.
    """)

@bot.on_message(filters.command("setchannel"))
async def set_channel(bot: Client, m: Message):
    await m.reply_text(
        "Send the channel username (e.g., `@channelusername`), ID (`-1001234567890`), or invite link (e.g., `https://t.me/joinchat/...`)."
    )
    input: Message = await bot.listen(m.chat.id)
    channel_input = input.text.strip()

    try:
        # Detect if input is an invite link
        if "t.me/" in channel_input or "joinchat" in channel_input:
            # Join the channel using invite link
            chat = await bot.join_chat(channel_input)
        else:
            # Treat as username or ID
            chat = await bot.get_chat(channel_input)

        # Check bot's privileges
        member = await bot.get_chat_member(chat.id, bot.me.id)
        if not member.privileges or not member.privileges.can_post_messages:
            raise ValueError(
                "Bot does not have 'Post Messages' permission in this channel."
            )

        # Save the channel ID for the user
        user_channels[m.from_user.id] = chat.id
        await m.reply_text(f"Channel successfully set: `{chat.title}`")
    except Exception as e:
        await m.reply_text(f"Error: {e}")

@bot.on_message(filters.command("showchannel"))
async def show_channel(bot: Client, m: Message):
    channel = user_channels.get(m.from_user.id, None)
    if channel:
        await m.reply_text(f"Your current channel: `{channel}`")
    else:
        await m.reply_text("You have not set a channel yet. Use `/setchannel`.")

@bot.on_message(filters.command("stop"))
async def stop_command(bot: Client, m: Message):
    if m.from_user.id in active_users:
        active_users.remove(m.from_user.id)
        await m.reply_text("✅ Bot operation has been stopped for your session.")
    else:
        await m.reply_text("❌ No active bot operation to stop.")

@bot.on_message(filters.command(["crchoudhary"]))
async def download_files(bot: Client, m: Message):
    active_users.add(m.from_user.id)
    editable = await m.reply_text("Send a TXT file containing the links.")
    input: Message = await bot.listen(editable.chat.id)
    file_path = await input.download()
    await input.delete()

    try:
        with open(file_path, "r") as f:
            links = [line.strip() for line in f.readlines()]
        os.remove(file_path)
    except Exception as e:
        await m.reply_text(f"Error reading file: {e}")
        active_users.remove(m.from_user.id)
        return

    await editable.edit(f"**Links Found:** `{len(links)}`\nSend the starting index (default: 1).")
    input_start: Message = await bot.listen(editable.chat.id)
    start_index = int(input_start.text.strip()) - 1
    await input_start.delete()

    await editable.edit("Enter a **batch name** for the files.")
    input_batch: Message = await bot.listen(editable.chat.id)
    batch_name = input_batch.text.strip()
    await input_batch.delete()

    await editable.edit("Choose the video resolution:\n144, 240, 360, 480, 720, 1080.")
    input_res: Message = await bot.listen(editable.chat.id)
    resolution = input_res.text.strip()
    await input_res.delete()

    await editable.edit("Send a **caption** for the files.")
    input_caption: Message = await bot.listen(editable.chat.id)
    caption_template = input_caption.text.strip()
    await input_caption.delete()

    await editable.edit("Send a thumbnail URL or type 'no' to skip.")
    input_thumb: Message = await bot.listen(editable.chat.id)
    thumb_url = input_thumb.text.strip()
    await input_thumb.delete()

    # Download thumbnail
    thumbnail = None
    if thumb_url.lower() != "no":
        getstatusoutput(f"wget '{thumb_url}' -O 'thumb.jpg'")
        thumbnail = "thumb.jpg"

    await editable.delete()
    target_channel = user_channels.get(m.from_user.id, "@DefaultChannelUsername")

    count = start_index + 1
    for i in range(start_index, len(links)):
        if m.from_user.id not in active_users:
            await m.reply_text("❌ Process stopped by the user.")
            break

        url = links[i]
        file_name = f"{str(count).zfill(3)} - {batch_name}"
        try:
            # Determine format for downloading
            if "youtu" in url:
                cmd = f'yt-dlp -o "{file_name}.mp4" -f "b[height<={resolution}]" "{url}"'
            elif ".pdf" in url:
                cmd = f'yt-dlp -o "{file_name}.pdf" "{url}"'
            elif "drive.google.com" in url:
                cmd = f'yt-dlp -o "{file_name}" "{url}"'
            elif "classplus" in url or "visionias" in url:
                cmd = f'yt-dlp -o "{file_name}.mp4" "{url}"'
            else:
                cmd = f'yt-dlp -o "{file_name}.mp4" "{url}"'

            os.system(cmd)

            # Prepare captions
            if url.endswith(".pdf"):
                caption = f"**📁 PDF File**\n**Batch:** `{batch_name}`\n**Filename:** `{file_name}.pdf`\n**Join:** @targetallcourse"
                await bot.send_document(target_channel, document=f"{file_name}.pdf", caption=caption)
                os.remove(f"{file_name}.pdf")
            else:
                caption = f"**📹 Video File**\n**Batch:** `{batch_name}`\n**Resolution:** `{resolution}p`\n**Filename:** `{file_name}.mkv`\n**Join:** @targetallcourse"
                await bot.send_video(target_channel, video=f"{file_name}.mkv", caption=caption, thumb=thumbnail)
                os.remove(f"{file_name}.mkv")

            count += 1
        except Exception as e:
            await m.reply_text(f"Error processing {url}: {e}")
            continue

    if thumbnail:
        os.remove(thumbnail)
    await m.reply_text("✅ All files have been processed successfully.")
    active_users.remove(m.from_user.id)

bot.run()
