import os
import asyncio
from config import LOG_FILE, DISCORD_CHANNEL_ID, ICONS, EMOTE_MAP
from discord.ext import commands
from discord import Embed, Color

LAST_LOG_POS = 0

def ingame_to_discord(msg: str) -> str:
    for discord_icon, ingame_char in EMOTE_MAP.items():
        msg = msg.replace(ingame_char, discord_icon)
    return msg

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

                        # Bỏ qua nếu bắt đầu bằng  và có , và nó nằm đúng ở đầu chuỗi
                        if msg.startswith("\ue100") and "\ue101" in msg:
                            end_idx = msg.index("\ue101")
                            start_idx = 0
                            if msg.startswith("\ue100"):
                                # Toàn bộ nội dung trước  là hệ thống gửi
                                system_text = msg[start_idx + 1 : end_idx]
                                # Nếu sau  chỉ là toạ độ/mã map thì bỏ qua toàn bộ
                                after = msg[end_idx + 1:].strip()
                                if not after or after.startswith("{"):
                                    continue  # hoặc continue nếu trong vòng lặp

                        msg = ingame_to_discord(msg)
                        await channel.send(f"{ICONS['say']} **{name}**: {msg}")


                elif "[Announcement]" in line and "[DISCORD]" not in line:
                    ann = line.split("[Announcement]")[-1].strip()
                    if ann.startswith("[THÔNG BÁO]"):
                        ann = ann[len("[THÔNG BÁO]"):].strip()
                    if ann:
                        if " đã tiêu diệt " in ann:
                            embed = Embed(
                                description=f"{ICONS['boss_kill']} {ann}",
                                color=Color.green()
                            )
                            await channel.send(embed=embed)
                        else:
                            await channel.send(f"{ICONS['announce']} {ann}")

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
                elif "[Death Announcement]" in line:
                    try:
                        content = line.split("[Death Announcement]")[-1].strip()
                        if " was " in content:
                            name, rest = content.split(" was ", 1)
                            embed = Embed(
                                description=f"{ICONS['death']} **{name.strip()}** was {rest.strip()}",
                                color=Color.red()
                            )
                            await channel.send(embed=embed)
                    except Exception as e:
                        print(f"❌ Lỗi xử lý Death Announcement: {e}")
                elif "[Resurrect Announcement]" in line:
                    try:
                        content = line.split("[Resurrect Announcement]")[-1].strip()
                        if " was " in content:
                            name, rest = content.split(" was ", 1)
                            embed = Embed(
                                description=f"{ICONS['resurrect']} **{name.strip()}** was {rest.strip()}",
                                color=Color.blue()
                            )
                            await channel.send(embed=embed)
                        else:
                            print(f"⚠️ Không tìm thấy cụm ' was ' trong dòng: {content}")
                    except Exception as e:
                        print(f"❌ Lỗi xử lý Resurrect Announcement: {e}")

        except Exception as e:
            print(f"Lỗi đọc log chat: {e}")
        await asyncio.sleep(1)