import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import time
import asyncio
import requests
import signal
import sys
import json5

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

bot = commands.Bot(command_prefix="!", self_bot=True)

with open("preferences.jsonc", "r", encoding="utf-8") as file:
    preferences = json5.load(file)

check_delay = preferences["check_delay"]
log_changes = preferences["log_changes"]
lyrics = preferences["lyrics"]
target_song = preferences["target_song"]
lyric_format = preferences["lyric_format"]
status_emoji = preferences["status_emoji"]
default_status = preferences["default_status"]

current_time = 0
lyrics_displaying = False
current_lyric = None
default_status_displaying = False

async def update_status():
    global default_status_displaying

    if current_lyric == None:
        return
    
    default_status_displaying = False

    requests.patch("https://discord.com/api/v9/users/@me/settings", headers={
        "Authorization": DISCORD_TOKEN,
        "Content-Type": "application/json"
    }, json={
        "custom_status": {
            "text": lyric_format.replace("$LYRIC$", current_lyric),
            "emoji_name": status_emoji["name"],
            "emoji_id": status_emoji["id"]
        }
    })

    if log_changes:
        print(f"Updated status with: {lyric_format.replace("$LYRIC$", current_lyric)}")

def reset_status():
    global default_status_displaying

    default_status_displaying = True

    requests.patch("https://discord.com/api/v9/users/@me/settings", headers={
        "Authorization": DISCORD_TOKEN,
        "Content-Type": "application/json"
    }, json={
        "custom_status": {
            "text": default_status["text"],
            "emoji_name": default_status["emoji"]["name"],
            "emoji_id": default_status["emoji"]["id"]
        }
    })

    print(f"Updated status with: {default_status['text']}")

async def display_lyrics():
    global current_time
    global current_lyric

    while True:
        if lyrics_displaying:
            new_lyric = None
            for i in range(len(lyrics) - 1):
                if current_time >= lyrics[-1][0]:
                    new_lyric = lyrics[-1][1]
                    break
                elif current_time >= lyrics[i][0] and current_time < lyrics[i + 1][0]:
                    new_lyric = lyrics[i][1]
                    break
            if new_lyric == None:
                if not default_status_displaying:
                    reset_status()
            if not new_lyric == current_lyric:
                current_lyric = new_lyric
                await update_status()
        else:
            print("off")
        await asyncio.sleep(.1)
        current_time += .1

async def check_activity():
    global current_time
    global lyrics_displaying

    for activity in bot.activities:
        if activity.name == "SoundCloud":
            if activity.details == target_song:
                current_time = time.time() - activity.timestamps.start.timestamp()
                if not lyrics_displaying:
                    lyrics_displaying = True
                return

    if not lyrics_displaying:
        return

    lyrics_displaying = False
    reset_status()

@bot.event
async def on_ready():
    asyncio.create_task(display_lyrics())

    while True:
        await check_activity()
        await asyncio.sleep(check_delay)

def on_exit(signum, frame):
    if not default_status_displaying:
        reset_status()
    sys.exit(0)

signal.signal(signal.SIGINT, on_exit)

bot.run(DISCORD_TOKEN)