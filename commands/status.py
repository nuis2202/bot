import discord
import json
import os
import datetime
from discord.ext import commands
from config import STATUS_FILE, PLAYER_ONLINE_FILES

class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="status")
    async def status(self, ctx):

        if not os.path.exists(STATUS_FILE):
            await ctx.send("❌ Không tìm thấy status.json.")
            return

        try:
            with open(STATUS_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # Tìm dòng KLEI mới nhất có current_day
            data = None
            for line in reversed(lines):
                if line.startswith("KLEI") and "current_day" in line:
                    _, _, json_str = line.partition("KLEI     1")
                    data = json.loads(json_str.strip())
                    break

            if not data:
                await ctx.send("⚠️ Không tìm thấy dữ liệu trạng thái.")
                return

            # Lấy thời gian và ngày
            time_str = self.seconds_to_clock(data.get("time", 0) % 480)
            season = data.get("season", "Unknown").capitalize()
            day = data.get("current_day", "?")
            days_remaining = data.get("days_remaining", "?")
            world_players = {}

            for world, file_path in PLAYER_ONLINE_FILES.items():
                players = []
                if os.path.exists(file_path):
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            raw_players = data.get("players", [])
                            players = [
                                f"• {p['name']} ({p['prefab']})"
                                for p in raw_players
                                if "name" in p and "prefab" in p
                            ]
                    except (json.JSONDecodeError, IOError):
                        pass
                world_players[world] = players
            all_worlds_text = []
            for world, players in world_players.items():
                if players:
                    text = f"🌍 **{world}**\n" + "\n".join(players)
                else:
                    text = f"🌍 **{world}**\nKhông có ai online."
                all_worlds_text.append(text)

            embed = discord.Embed(
                title="🌐 No Mud Status",
                color=discord.Color.blurple()
            )
            # embed.add_field(name="⏰ Time of Day", value=time_str, inline=True)
            # embed.add_field(name="Thông tin chung", value=info_table, inline=False)
            embed.add_field(name="📅 Day", value=str(day), inline=True)
            embed.add_field(name="🍂 Season   ", value=season, inline=True)
            embed.add_field(name="⏳ Days Left", value=str(days_remaining), inline=True)
            for world, players in world_players.items():
                player_count = len(players)
                player_text = "\n".join(players) if players else "Không có ai online."
                
                embed.add_field(
                    name=f"👥 {world} ({player_count})",
                    value=player_text,
                    inline=False
                )
            embed.set_footer(text="Create by Siun")
            embed.timestamp = datetime.datetime.now()

            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send("❌ Lỗi khi xử lý dữ liệu trạng thái.")
            print(f"Lỗi status: {e}")

    def seconds_to_clock(self, sec):
        minutes = (sec // 8) % 60
        hours = (sec // 480) * 24 + (sec // 60)
        return f"{int(hours):02}:{int(minutes):02}"

async def setup(bot):
    await bot.add_cog(Status(bot))
