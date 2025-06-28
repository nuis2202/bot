import os

DISCORD_BOT_TOKEN = "TOKEN" # bot token
DISCORD_CHANNEL_ID = 123456789 # channel bot phản hồi

CLUSTER_FOLDER = r"\Documents\Klei\DoNotStarveTogether\DediServer" # thay đổi lại đường dẫn tới file save game
MASTER_FOLDER = os.path.join(CLUSTER_FOLDER, r"Shard1") #  shard master
LOG_FILE = os.path.join(MASTER_FOLDER, r"server_chat_log.txt")
JSON_FILE = os.path.join(MASTER_FOLDER, r"save\cmd_queue.json")
QUEUE_FILE = os.path.join(MASTER_FOLDER, r"save\chat_queue.json")
FLAG_FILE = os.path.join(MASTER_FOLDER, r"save\rollback_flag.json")

ALLOWED_ROLE_IDS = [123456, 123456] # role ID dùng cho rollback

# custom icon
ICONS = {
    "join": "<:z_boxin:1386190260718927922>",
    "leave": "<:z_boxout:1386190353635217479>",
    "say": "<:p_bubbleheart:1386103088661921843>",
    "announce": "📢",
    "boss_kill": "<:z_exclamation:1375742800498524230>",
    "agree": "<:z_agree:1385938128363192470>",
    "disagree": "<:z_x:1373524879390937140>"
}
