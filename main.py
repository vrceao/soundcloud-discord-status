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

target_song = preferences["target_song"]
path = f"songs/{target_song}.jsonc"
if not os.path.exists(path):
    print(f"{path} not found")
    sys.exit(0)
with open(path, "r", encoding="utf-8") as file:
    song = json5.load(file)

activity_check_delay = preferences["activity_check_delay"]
lyric_change_check_delay = preferences["lyric_change_check_delay"]
log_changes = preferences["log_changes"]
lyric_format = preferences["lyric_format"]
status_emoji = preferences["status_emoji"]
default_status = preferences["default_status"]
reset_status_on_no_lyric = preferences["reset_status_on_no_lyric"]
reset_status_on_inactive = preferences["reset_status_on_inactive"]
reset_status_on_exit = preferences["reset_status_on_exit"]

target_title = song["target_title"]
lyrics = song["lyrics"]

for i in range(len(lyrics) - 1):
    if not i == len(lyrics) - 1 and lyrics[i]["timestamp"][1] == -1:
        lyrics[i]["timestamp"][1] = lyrics[i + 1]["timestamp"][0]

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

    if log_changes:
        print(f"Updated status with: {default_status['text']}")

async def display_lyrics():
    global current_time
    global current_lyric

    while True:
        if lyrics_displaying:
            new_lyric = None
            for i in range(len(lyrics)):
                if lyrics[i]["timestamp"][1] == -1:
                    if current_time >= lyrics[i]["timestamp"][0]:
                        new_lyric = lyrics[i]["text"]
                elif current_time >= lyrics[i]["timestamp"][0] and current_time < lyrics[i]["timestamp"][1]:
                    new_lyric = lyrics[i]["text"]
                    break
            if new_lyric == None:
                if not default_status_displaying and reset_status_on_no_lyric:
                    reset_status()
            if not new_lyric == current_lyric:
                current_lyric = new_lyric
                await update_status()

        await asyncio.sleep(lyric_change_check_delay)
        current_time += lyric_change_check_delay

async def check_activity():
    global current_time
    global lyrics_displaying

    soundcloud_found = False

    for activity in bot.activities:
        if activity.name == "SoundCloud":
            soundcloud_found = True
            if activity.details == target_title:
                current_time = time.time() - activity.timestamps.start.timestamp()
                if not lyrics_displaying:
                    print("Song detected, displaying lyrics now")
                    lyrics_displaying = True
                return
            else:
                print("You're not listening to the target song")

    if not soundcloud_found:
        print("SoundCloud isn't on your Discord activity")

    if not lyrics_displaying:
        return

    lyrics_displaying = False

    if reset_status_on_inactive:
        reset_status()

@bot.event
async def on_ready():
    asyncio.create_task(display_lyrics())

    while True:
        await check_activity()
        await asyncio.sleep(activity_check_delay)

def on_exit(signum, frame):
    if not default_status_displaying and reset_status_on_exit:
        print("Exiting")
        reset_status()
    sys.exit(0)

signal.signal(signal.SIGINT, on_exit)

bot.run(DISCORD_TOKEN)