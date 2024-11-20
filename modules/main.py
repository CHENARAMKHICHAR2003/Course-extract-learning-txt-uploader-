import os
import re
import requests
from aiohttp import ClientSession
from pyrogram import Client, filters
from pyrogram.types import Message
from subprocess import getstatusoutput

# Initialize the bot
API_ID = "your_api_id"
API_HASH = "your_api_hash"
BOT_TOKEN = "your_bot_token"

bot = Client("crchoudhary_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# To store channel configuration
CHANNELS = {}


# Start command
@bot.on_message(filters.command("start") & filters.private)
async def start(client, message: Message):
    await message.reply_text(
        f"**Hello {message.from_user.first_name}!**\n"
        "Welcome to the **CR Choudhary Bot**.\n"
        "Use `/help` to see the available commands."
    )


# Help command
@bot.on_message(filters.command("help") & filters.private)
async def help_command(client, message: Message):
    await message.reply_text(
        "**Here are the available commands:**\n"
        "/crchoudhary - Process links from a text file.\n"
        "/setchannel - Set a channel to post updates.\n"
        "/showchannel - Show the current set channel.\n"
        "/help - Show this help message."
    )


# SetChannel command
@bot.on_message(filters.command("setchannel") & filters.private)
async def set_channel(client, message: Message):
    global CHANNELS
    await message.reply_text("**Please send me the channel ID or username.**")
    response = await bot.listen(message.chat.id)

    channel_id = response.text
    CHANNELS[message.chat.id] = channel_id

    await message.reply_text(f"**Channel set to:** `{channel_id}`")
    await response.delete()


# ShowChannel command
@bot.on_message(filters.command("showchannel") & filters.private)
async def show_channel(client, message: Message):
    global CHANNELS
    channel = CHANNELS.get(message.chat.id, "No channel set.")
    await message.reply_text(f"**Current Channel:** `{channel}`")


# CR Choudhary Command (Process Links)
@bot.on_message(filters.command("crchoudhary") & filters.private)
async def process_links(client, message: Message):
    editable = await message.reply_text("**Please send me a text file containing links.**")
    input_file = await bot.listen(message.chat.id)

    # Validate input file
    if input_file.document:
        file_path = await bot.download_media(input_file.document)
        x = file_path
    else:
        await editable.edit("❌ Please send a valid text file.")
        return

    try:
        # Read and process the input file for links
        with open(x, "r") as f:
            content = f.read()
        content = content.split("\n")
        links = []
        for i in content:
            links.append(i.split("://", 1))
        os.remove(x)
    except:
        await editable.edit("**Invalid file input.**")
        os.remove(x)
        return

    await editable.edit(
        f"**𝕋ᴏᴛᴀʟ ʟɪɴᴋ𝕤 ғᴏᴜɴᴅ ᴀʀᴇ🔗🔗** **{len(links)}**\n\n"
        "**𝕊ᴇɴᴅ 𝔽ʀᴏᴍ ᴡʜᴇʀᴇ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ɪɴɪᴛɪᴀʟ ɪ𝕤** **1**"
    )
    input0: Message = await bot.listen(editable.chat.id)
    raw_text = input0.text
    await input0.delete(True)

    await editable.edit("**Now Please Send Me Your Batch Name**")
    input1: Message = await bot.listen(editable.chat.id)
    raw_text0 = input1.text
    await input1.delete(True)

    await editable.edit("**𝔼ɴᴛᴇʀ ʀᴇ𝕤ᴏʟᴜᴛɪᴏɴ📸**\n144,240,360,480,720,1080 please choose quality")
    input2: Message = await bot.listen(editable.chat.id)
    raw_text2 = input2.text
    await input2.delete(True)

    try:
        resolutions = {
            "144": "256x144",
            "240": "426x240",
            "360": "640x360",
            "480": "854x480",
            "720": "1280x720",
            "1080": "1920x1080",
        }
        res = resolutions.get(raw_text2, "UN")
    except Exception:
        res = "UN"

    await editable.edit("Now Enter A Caption to add caption on your uploaded file")
    input3: Message = await bot.listen(editable.chat.id)
    raw_text3 = input3.text
    await input3.delete(True)
    highlighter = f"️ ⁪⁬⁮⁮⁮"
    MR = highlighter if raw_text3 == "Robin" else raw_text3

    await editable.edit("Now send the Thumb URL or type `no` if you don't want a thumbnail.")
    input6 = await bot.listen(editable.chat.id)
    thumb = input6.text
    await input6.delete(True)

    if thumb.startswith("http://") or thumb.startswith("https://"):
        getstatusoutput(f"wget '{thumb}' -O 'thumb.jpg'")
        thumb = "thumb.jpg"
    else:
        thumb = None

    if len(links) == 1:
        count = 1
    else:
        count = int(raw_text)

    await editable.edit(f"Starting processing of {len(links)} links...")

    # Process the links
    for i in range(count - 1, len(links)):
        url = "https://" + links[i][1]
        
        # VisionIAS URL processing
        if "visionias" in url:
            async with ClientSession() as session:
                async with session.get(url, headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                    'Accept-Language': 'en-US,en;q=0.9', 'Cache-Control': 'no-cache', 'Connection': 'keep-alive', 'Pragma': 'no-cache',
                    'Referer': 'http://www.visionias.in/', 'Sec-Fetch-Dest': 'iframe', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Site': 'cross-site',
                    'Upgrade-Insecure-Requests': '1', 'User-Agent': 'Mozilla/5.0 (Linux; Android 12; RMX2121) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36',
                    'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"', 'sec-ch-ua-mobile': '?1', 'sec-ch-ua-platform': '"Android"',
                }) as resp:
                    text = await resp.text()
                    url = re.search(r"(https://.*?playlist.m3u8.*?)\"", text).group(1)

        elif 'videos.classplusapp' in url:
            # ClassPlusApp URL processing
            url = requests.get(
                f'https://api.classplusapp.com/cams/uploader/video/jw-signed-url?url={url}',
                headers={'x-access-token': 'your_access_token_here'}
            ).json()['url']

        elif '/master.mpd' in url:
            # MPD URL processing (for adaptive streaming)
            id = url.split("/")[-2]
            url = "https://d26g5bnklkwsh4.cloudfront.net/" + id + "/master.m3u8"

        elif 'drive.google.com' in url:
            # Google Drive URL processing
            url = url.replace("drive.google.com/file/d/", "drive.google.com/uc?export=download&id=")

        elif 'youtube' in url or 'youtu.be' in url:
            # YouTube URL processing
            if "youtu" in url:
                ytf = f"b[height<={raw_text2}][ext=mp4]/bv[height<={raw_text2}][ext=mp4]+ba[ext=m4a]/b[ext=mp4]"
            else:
                ytf = f"b[height<={raw_text2}]/bv[height<={raw_text2}]+ba/b/bv+ba"

            if "jw-prod" in url:
                cmd = f'yt-dlp -o "{name}.mp4" "{url}"'
            else:
                cmd = f'yt-dlp -f "{ytf}" "{url}" -o "{name}.mp4"'

        elif 'vimeo.com' in url:
            # Vimeo URL processing
            cmd = f'yt-dlp -f bestvideo+bestaudio "{url}" -o "{name}.mp4"'

        else:
            # Default case if no specific condition is matched
            url = url.strip()

        # After URL processing, continue with the remaining download logic:
        name1 = links[i][0].replace("\t", "").replace(":", "").replace("/", "").replace("+", "").replace("#", "").replace("|", "").replace("@", "").replace("*", "").replace(".", "").replace("https", "").replace("http", "").strip()
        name = f'{str(count).zfill(3)}) {name1[:60]}'

        # Execute the download command if needed
        if cmd:
            os.system(cmd)  # Or use an appropriate method to execute commands based on your system

        # Optionally, add a message to let the user know about the progress or status
        await bot.send_message(
            message.chat.id,
            f"Processing: `{url}`\nResolution: `{res}`\nCaption: `{MR}`"
        ) 

    await editable.edit("**Processing complete!**")

# Run the bot
bot.run()
