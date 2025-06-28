import time
import json
import os
import re
from discord.ext import commands
from config import ICONS, ALLOWED_ROLE_IDS
from utils.command_writer import write_command

ROLLBACK_COOLDOWN = 60
ROLLBACK_TIME_FILE = "data/rollback_time.json"

def load_last_rollback_time():
    try:
        with open(ROLLBACK_TIME_FILE, "r", encoding="utf-8") as f:
            return json.load(f).get("last_rollback", 0)
    except:
        return 0

def save_last_rollback_time(timestamp):
    os.makedirs(os.path.dirname(ROLLBACK_TIME_FILE), exist_ok=True)
    with open(ROLLBACK_TIME_FILE, "w", encoding="utf-8") as f:
        json.dump({"last_rollback": timestamp}, f)

class Rollback(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_rollback_time = load_last_rollback_time()

    @commands.command(name="rollback")
    async def rollback(self, ctx, *, raw: str):
        raw = raw.strip()

        # Trường hợp confirm
        if raw.startswith("confirm"):
            match = re.search(r"\d+", raw)
            if not match:
                await ctx.send(f"{ICONS['disagree']} Xác nhận rollback cần có số.")
                return
            num = int(match.group(0))
            await self.perform_rollback(ctx, num, confirmed=True)
            return

        # Trường hợp rollback thường
        match = re.search(r"\d+", raw)
        if not match:
            await ctx.send(f"{ICONS['disagree']} Vui lòng chỉ nhập số rollback.")
            return

        num = int(match.group(0))
        if num > 5:
            await ctx.send(f"{ICONS['disagree']} Bạn có chắc muốn rollback {num} ngày không?\nGõ `!rollback confirm {num}` để xác nhận.")
            return

        await self.perform_rollback(ctx, num)

    async def perform_rollback(self, ctx, num, confirmed=False):
        now = time.time()
        if now - self.last_rollback_time < ROLLBACK_COOLDOWN:
            wait_time = int(ROLLBACK_COOLDOWN - (now - self.last_rollback_time))
            await ctx.send(f"{ICONS['disagree']} Vui lòng đợi {wait_time} giây nữa.")
            return

        if not any(role.id in ALLOWED_ROLE_IDS for role in ctx.author.roles):
            await ctx.send(f"{ICONS['disagree']} Bạn chưa đủ quyền.")
            return

        if num < 1:
            await ctx.send(f"{ICONS['disagree']} Số ngày rollback phải từ 1 trở lên.")
            return

        if num > 5 and not confirmed:
            await ctx.send(f"{ICONS['disagree']} Gõ `!rollback confirm {num}` để xác nhận rollback lớn hơn 5.")
            return

        command = f"c_rollback({num})"
        if await write_command(command):
            self.last_rollback_time = now
            save_last_rollback_time(now)
            await ctx.send(f"{ICONS['agree']} Đã gửi: {command}")
        else:
            await ctx.send(f"{ICONS['disagree']} Gửi lệnh thất bại.")

async def setup(bot):
    await bot.add_cog(Rollback(bot))
