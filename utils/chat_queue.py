import os
import json
from config import QUEUE_FILE, EMOTE_MAP

def discord_to_ingame(msg: str) -> str:
    for discord_icon, ingame_char in EMOTE_MAP.items():
        msg = msg.replace(discord_icon, ingame_char)
    return msg

async def write_discord_message(author, content):
    try:
        content = discord_to_ingame(content)
        queue = []
        if os.path.exists(QUEUE_FILE):
            try:
                with open(QUEUE_FILE, "r", encoding="utf-8") as f:
                    raw = f.read().strip()
                    if raw.startswith("KLEI"):
                        raw = raw[10:]
                    queue = json.loads(raw)
            except json.JSONDecodeError:
                print("⚠️ queue.json bị lỗi hoặc rỗng → tạo mới.")
                queue = []

        queue.append({"from": author, "text": content})
        with open(QUEUE_FILE, "w", encoding="utf-8") as f:
            json.dump(queue, f, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Lỗi ghi queue.json: {e}")
        return False
