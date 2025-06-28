import discord
import datetime
import json
import os
import asyncio
from discord.ext import commands, tasks
from config import STATUS_CHANNEL_ID, STATUS_FILE, PLAYER_ONLINE_FILES, ICONS, STATUS_MSG_FILE, SEASON_NAMES

def read_klei_json(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            line = f.read().strip()
            if line.startswith("KLEI") and "{" in line:
                json_str = line[line.find("{"):]
                return json.loads(json_str)
    except Exception as e:
        print(f"[Lỗi] Không đọc được {filepath}: {e}")
    return {}

class StatusLoop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.status_message = None  # tin nhắn sẽ được edit
        self.bot.loop.create_task(self.load_status_message())
        self.status_updater.start()

    def cog_unload(self):
        self.status_updater.cancel()
    
    async def load_status_message(self):
        """Tải lại tin nhắn từ file ID nếu có"""
        await self.bot.wait_until_ready()
        if os.path.exists(STATUS_MSG_FILE):
            try:
                with open(STATUS_MSG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                channel = self.bot.get_channel(STATUS_CHANNEL_ID)
                if channel:
                    self.status_message = await channel.fetch_message(data["message_id"])
                    print(f"[StatusLoop] Đã khôi phục status_message ID {data['message_id']}")
            except Exception as e:
                print(f"[StatusLoop] Không thể khôi phục status_message: {e}")

    @tasks.loop(minutes=1)
    async def status_updater(self):
        channel = self.bot.get_channel(STATUS_CHANNEL_ID)
        if channel is None:
            return
        await asyncio.sleep(1)

        if not os.path.exists(STATUS_FILE):
            await channel.send("❌ Không tìm thấy status.json.")
            return

        try:
            with open(STATUS_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()
            data = None
            for line in reversed(lines):
                if line.startswith("KLEI") and "current_day" in line:
                    _, _, json_str = line.partition("KLEI     1")
                    data = json.loads(json_str.strip())
                    break

            if not data:
                await channel.send("⚠️ Không tìm thấy dữ liệu trạng thái.")
                return
            # Lấy thời gian và ngày
            # time_str = self.seconds_to_clock(data.get("time", 0) % 480)
            season = data.get("season", "Unknown").lower()
            day = data.get("current_day", "?")
            days_remaining = data.get("days_remaining", "?")
            # Danh sách người chơi
            world_players = {}

            for world, file_path in PLAYER_ONLINE_FILES.items():
                players = []
                if os.path.exists(file_path):
                    try:
                        data = read_klei_json(file_path)
                        raw_players = data.get("players", [])
                        try:
                            players = [
                                f"{ICONS[p['prefab']]} {p['name']} ({p['days_survived'] + 1})"
                                for p in raw_players
                                if "name" in p and "prefab" in p
                            ]
                        except:
                            players = [
                                f"({p['prefab']}) {p['name']} ({p['days_survived'] + 1})"
                                for p in raw_players
                                if "name" in p and "prefab" in p
                            ]
                    except (json.JSONDecodeError, IOError):
                        pass
                world_players[world] = players

            # 📝 Tạo chuỗi hiển thị cho từng world
            all_worlds_text = []
            for world, players in world_players.items():
                if players:
                    text = f"{ICONS['world']} **{world}**\n" + "\n".join(players)
                else:
                    text = f"{ICONS['world']} **{world}**\nKhông có ai online."
                all_worlds_text.append(text)

            embed = discord.Embed(
                title="🌐 No Mud Status",
                color=discord.Color.blurple()
            )

            embed.add_field(name=f"{ICONS['calendar']} Day", value=str(day), inline=True)
            embed.add_field(name=f"{ICONS[season]} Season", value=SEASON_NAMES[season], inline=True)
            embed.add_field(name=f"{ICONS['clock']} Days Left", value=str(days_remaining), inline=True)
            for world, players in world_players.items():
                player_count = len(players)
                player_text = "\n".join(players) if players else "Không có ai online."
                
                embed.add_field(
                    name=f"{ICONS['world']} {world} ({player_count})",
                    value=player_text,
                    inline=False
                )
            embed.set_footer(text="Create by Siun")
            embed.timestamp = datetime.datetime.now()
            if self.status_message is None:
                self.status_message = await channel.send(embed=embed)
                with open(STATUS_MSG_FILE, "w") as f:
                    json.dump({"message_id": self.status_message.id}, f)
            else:
                await self.status_message.edit(embed=embed)

        except Exception as e:
            await channel.send("❌ Lỗi khi xử lý dữ liệu trạng thái.")
            print(f"Lỗi status: {e}")

    @commands.command(name="statusloop")
    async def manual_start_status(self, channel):
        """Gửi status lần đầu (nếu cần khởi động bằng lệnh)"""
        # await channel.send("✅ Bắt đầu cập nhật status mỗi phút.")
        # self.status_message = await channel.send("Đang lấy trạng thái...")
        await self.status_updater()  # chạy ngay lần đầu

async def setup(bot):
    await bot.add_cog(StatusLoop(bot))