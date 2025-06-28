import json
import os
from config import JSON_FILE

async def write_command(command):
    try:
        with open(JSON_FILE, "w", encoding="utf-8") as f:
            json.dump({"command": command, "discord_msg": None}, f, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Lỗi ghi cmd_queue.json: {e}")
        return False
