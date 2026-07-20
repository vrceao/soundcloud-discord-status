This is a Discord self-bot that automatically changes your status with the lyrics of the song you're currently listening to on SoundCloud

**This script requires the PreMiD web extension to capture the song from your Discord status** https://premid.app/ (Make sure to enable SoundCloud in PreMiD settings and authorize it with your Discord account)

# Setup

```bash
git clone https://github.com/vrceao/soundcloud-discord-status
cd soundcloud-discord-status
cp .env.example .env
```

- Put your discord token in the .env file
- Check out preferences.jsonc to customize it to your liking

```bash
py main.py
```

# Contributing

- If someone knows how to use websocket instead of using discord.py-self, please reach out
- Adding building so it's possible to have just one exe maybe even with a gui