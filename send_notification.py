import sys
import os
import requests

domain = sys.argv[1]
file_path = sys.argv[2]

bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")

with open(file_path, "r") as f:
    lines = f.readlines()

if lines:
    message = f"🔎 Recon results for *{domain}*:\n" + "".join(f"- `{line.strip()}`\n" for line in lines[:10])
    if len(lines) > 10:
        message += f"... and {len(lines)-10} more."

    requests.post(
        f"https://api.telegram.org/bot{bot_token}/sendMessage",
        data={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    )
