import os
import json
from config import QUEUE_FILE

async def write_discord_message(author, content):
    try:
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
