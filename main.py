import os
import json
import discord
from discord.ext import commands
from config import DISCORD_BOT_TOKEN, DISCORD_CHANNEL_ID, JSON_FILE, QUEUE_FILE
from utils.watcher import log_watcher
from utils.chat_queue import write_discord_message

BOT_PREFIX = "!"
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

class MyBot(commands.Bot):
    async def setup_hook(self):
        for filename in os.listdir("./commands"):
            if filename.endswith(".py") and filename not in ("__init__.py"):
                try:
                    await self.load_extension(f"commands.{filename[:-3]}")
                except Exception as e:
                    print(f"❌ Failed to load commands {filename}: {e}")
        for filename in os.listdir("./tasks"):
            if filename.endswith(".py") and filename not in ("__init__.py"):
                try:
                    await bot.load_extension(f"tasks.{filename[:-3]}")
                except Exception as e:
                    print(f"❌ Failed to load task {filename}: {e}")

bot = MyBot(command_prefix=BOT_PREFIX, intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot đang chạy: {bot.user}")
    for file, default in [(JSON_FILE, {"command": "", "discord_msg": None}), (QUEUE_FILE, [])]:
        os.makedirs(os.path.dirname(file), exist_ok=True)
        if not os.path.exists(file):
            with open(file, "w", encoding="utf-8") as f:
                json.dump(default, f)
    bot.loop.create_task(log_watcher(bot))

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if message.channel.id == DISCORD_CHANNEL_ID:
        content = message.content.strip()
        if content.startswith(BOT_PREFIX):
            await bot.process_commands(message)
            return
        await write_discord_message(message.author.display_name, message.content.strip())
    await bot.process_commands(message)

bot.run(DISCORD_BOT_TOKEN)
