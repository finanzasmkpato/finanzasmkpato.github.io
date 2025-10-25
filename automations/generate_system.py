import yaml, pdfkit, random
from jinja2 import Template
from datetime import datetime
import requests, os

# === Config ===
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "@finanzas_mkpato")

# === Load actions ===
with open("data/actions.yml", "r", encoding="utf-8") as f:
    actions = yaml.safe_load(f)["systems"]

# Choose random or sequential
action = random.choice(actions)

# === Load HTML template ===
with open("templates/action_template.html", "r", encoding="utf-8") as f:
    template = Template(f.read())

html = template.render(**action)

# === Generate PDF ===
os.makedirs("outputs", exist_ok=True)
pdf_name = f"{action['title'].replace(' ', '_').lower()}.pdf"
pdf_path = f"outputs/{pdf_name}"
pdfkit.from_string(html, pdf_path)

# === Build Telegram message ===
message = f"""💰 {action['title']}

🎯 {action['objective']}

🧩 Pasos:
{chr(10).join(['- ' + s for s in action['steps']])}

🧠 Regla: {action['rule']}

🤖 Prompt IA: {action['prompt']}

📈 Métrica: {action['metric']}

👉 {action['cta']}
"""

# === Send to Telegram ===
def send_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    r = requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": text})
    r.raise_for_status()

def send_pdf():
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
    with open(pdf_path, "rb") as f:
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID}, files={"document": f})

if TELEGRAM_BOT_TOKEN:
    send_message(message)
    send_pdf()
    print(f"✅ Acción publicada: {action['title']}")
else:
    print("❌ Falta TELEGRAM_BOT_TOKEN o configuración del canal.")
