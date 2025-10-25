import yaml, pdfkit, random
from jinja2 import Template
from datetime import datetime
import requests

# === Config ===
TELEGRAM_BOT_TOKEN = "TU_TOKEN"
TELEGRAM_CHAT_ID = "@mkpato_pro"

# === Load system data ===
with open("data/systems.yml", "r", encoding="utf-8") as f:
    systems = yaml.safe_load(f)["systems"]

system = random.choice(systems)

# === Load HTML template ===
with open("templates/system_template.html", "r", encoding="utf-8") as f:
    template = Template(f.read())

html = template.render(**system)

# === Generate PDF ===
output_pdf = f"outputs/{system['title'].replace(' ', '-').lower()}.pdf"
pdfkit.from_string(html, output_pdf)

# === Telegram message ===
message = f"""💼 {system['title']}

🎯 {system['objective']}

📈 Métrica objetivo: {system['metric']}

🧠 Regla MkPato: {system['rule']}

📎 {system['cta']}
"""

# Send to Telegram
url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": message})

# Send PDF
files = {'document': open(output_pdf, 'rb')}
requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument", data={"chat_id": TELEGRAM_CHAT_ID}, files=files)
