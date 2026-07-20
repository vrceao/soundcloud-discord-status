This is a Discord self-bot that automatically changes your status with the lyrics of the song you're currently listening to on SoundCloud

This does not automatically fetch the lyrics, you need to fill them in manually, as well as the timestamps

# Setup

**This script requires the PreMiD web extension to capture the song from your Discord status** https://premid.app/ (Make sure to enable SoundCloud in PreMiD settings and authorize it with your Discord account)

The commands are for powershell, use common sense if you're using something different

```ps
git clone https://github.com/vrceao/soundcloud-discord-status
cd soundcloud-discord-status
copy .env.example .env
py -m pip install -r requirements.txt
```

- Put your discord token in the .env file (Do not share it with anyone!)

You're done!

```ps
py .\main.py
```

# Customization

After cloning, you're using my config

- Check out **preferences.jsonc** to customize everything
- Check out **songs/** to see examples of lyrics or make your own (`songs/misery.jsonc` contains comments, check it if you're planning on diving deeper)

# Contributing

- You can contribute by adding lyrics of any song, just double-check that the it's working correctly and timed properly

If someone has an idea how could websocket be used instead of discord.py-self, please reach out