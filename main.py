import os
import json
import discord
from discord.ext import commands
from config import DISCORD_BOT_TOKEN, DISCORD_CHANNEL_ID, JSON_FILE, QUEUE_FILE, ICONS, ALLOWED_ROLE_IDS, FLAG_FILE
from watcher import log_watcher
from commands import write_command
from chat_queue import write_discord_message

BOT_PREFIX = "!"
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

def is_rollback_in_progress():
    try:
        with open(FLAG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("rolling_back", False)
    except Exception:
        return False

bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents)

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

        if content.startswith("!rollback "):
            if is_rollback_in_progress():
                await message.channel.send(f"{ICONS['disagree']} Đang rollback rồi, hãy chờ rollback hiện tại hoàn tất.")
                return

            if not any(role.id in ALLOWED_ROLE_IDS for role in message.author.roles):
                await message.channel.send(f"{ICONS['disagree']} uh ou, bạn chưa đủ quyền hạn, hãy nhờ <@&1385907308235718656> rollback nhé !")
                return

            arg = content[len("!rollback "):].strip()
            if arg.isdigit() and 1 <= int(arg) <= 5:
                command = f"c_rollback({int(arg)})"

                # Ghi trạng thái rollback vào file
                with open(FLAG_FILE, "w", encoding="utf-8") as f:
                    json.dump({"rolling_back": True}, f)

                await write_command(command)
                await message.channel.send(f"{ICONS['agree']} Đã gửi: {command}")
            else:
                await message.channel.send(f"{ICONS['disagree']} Chỉ rollback từ 1 đến 5.")
            return

        await write_discord_message(message.author.display_name, content)

    await bot.process_commands(message)

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

bot.run(DISCORD_BOT_TOKEN)
