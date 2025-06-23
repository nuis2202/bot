import os
import asyncio
from config import LOG_FILE, DISCORD_CHANNEL_ID, ICONS
from discord.ext import commands

LAST_LOG_POS = 0

async def log_watcher(bot: commands.Bot):
    global LAST_LOG_POS
    await bot.wait_until_ready()
    channel = bot.get_channel(DISCORD_CHANNEL_ID)
    if not channel:
        print(f"❌ Không tìm thấy kênh với ID {DISCORD_CHANNEL_ID}")
        return

    if not os.path.exists(LOG_FILE):
        print(f"❌ Không tìm thấy file log: {LOG_FILE}")
        return

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        f.seek(0, os.SEEK_END)
        LAST_LOG_POS = f.tell()

    print("🟢 Đang theo dõi server_chat_log.txt")

    while not bot.is_closed():
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                f.seek(LAST_LOG_POS)
                lines = f.readlines()
                LAST_LOG_POS = f.tell()

            for line in lines:
                if "[Say] (" in line:
                    parts = line.split(") ")
                    if len(parts) >= 2 and ": " in parts[1]:
                        name, msg = parts[1].strip().split(": ", 1)
                        await channel.send(f"{ICONS['say']} **{name}**: {msg}")
                elif "[Announcement]" in line and "[DISCORD]" not in line:
                    ann = line.split("[Announcement]")[-1].strip()
                    if ann.startswith("[THÔNG BÁO]"):
                        ann = ann[len("[THÔNG BÁO]"):].strip()
                    elif ann.startswith("[Restart complete]"):
                        ann = f"**Máy chủ đã sẵn sàng để tham gia!**"
                    if ann:
                        await channel.send(f"📢 {ann}")
                elif "[Leave Announcement]" in line:
                    try:
                        player = line.split("[Leave Announcement]")[-1].strip()
                        if player:
                            await channel.send(f"{ICONS['leave']} **{player}** đã rời khỏi thế giới.")
                    except Exception as e:
                        print(f"❌ Lỗi xử lý Leave Announcement: {e}")
                elif "[Join Announcement]" in line:
                    try:
                        player = line.split("[Join Announcement]")[-1].strip()
                        if player:
                            await channel.send(f"{ICONS['join']} **{player}** đã tham gia thế giới No Mud!")
                    except Exception as e:
                        print(f"❌ Lỗi xử lý Join Announcement: {e}")

        except Exception as e:
            print(f"Lỗi đọc log chat: {e}")
        await asyncio.sleep(1)
