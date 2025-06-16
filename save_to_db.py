import psycopg2
import sys
import os
import requests

project_name = os.getenv("PROJECT_NAME") or "Default"
domain_name = sys.argv[1]
file_path = sys.argv[2]

def send_telegram(message):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    requests.post(
        f"https://api.telegram.org/bot{bot_token}/sendMessage",
        data={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    )

def get_http_info(url):
    try:
        r = requests.get(f"http://{url}", timeout=5)
        status = r.status_code
        title = None
        if "<title>" in r.text:
            title = r.text.split("<title>")[1].split("</title>")[0]
        return status, title
    except:
        return None, None

conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS"),
    host=os.getenv("DB_HOST"),
    port="5432"
)
cur = conn.cursor()

cur.execute("INSERT INTO projects (name) VALUES (%s) ON CONFLICT (name) DO NOTHING", (project_name,))
cur.execute("SELECT id FROM projects WHERE name = %s", (project_name,))
project_id = cur.fetchone()[0]

cur.execute("INSERT INTO domains (project_id, domain_name) VALUES (%s, %s) ON CONFLICT DO NOTHING RETURNING id", (project_id, domain_name,))
domain_id = cur.fetchone()[0] if cur.rowcount else None
if not domain_id:
    cur.execute("SELECT id FROM domains WHERE project_id = %s AND domain_name = %s", (project_id, domain_name))
    domain_id = cur.fetchone()[0]

with open(file_path, "r") as f:
    for line in f:
        sub = line.strip()
        if not sub:
            continue

        status, title = get_http_info(sub)

        cur.execute("SELECT id, status_code, title FROM subdomains WHERE domain_id = %s AND subdomain = %s", (domain_id, sub))
        result = cur.fetchone()

        if result:
            sub_id, old_status, old_title = result
            if old_status != status or old_title != title:
                cur.execute("UPDATE subdomains SET status_code = %s, title = %s WHERE id = %s", (status, title, sub_id))
                send_telegram(f"🔄 *Changed asset*\n`{sub}`\n*Status:* `{old_status}` → `{status}`\n*Title:* `{old_title}` → `{title}`")
        else:
            cur.execute(
                "INSERT INTO subdomains (domain_id, subdomain, status_code, title) VALUES (%s, %s, %s, %s)",
                (domain_id, sub, status, title)
            )
            send_telegram(f"🆕 *New asset found:*\n`{sub}`\n*Status:* `{status}`\n*Title:* `{title}`")

conn.commit()
cur.close()
conn.close()
