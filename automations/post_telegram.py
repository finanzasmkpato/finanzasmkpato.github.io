from pathlib import Path
import csv, os, requests, html

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "telegram_queue.csv"

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")  # ej. @finanzas_mkpato

def next_pending(rows):
    for i, r in enumerate(rows):
        if r.get("status","pending").lower() == "pending":
            return i, r
    return None, None

def quality_ok(title, body):
    body = (body or "").strip()
    if len(title.strip()) < 8: return False
    if len(body) < 220 or body.count(" ") < 40: return False
    if body.lower().count("claridad")>0: return False  # no quieres ese término
    return True

def build_html(title, body, cta=None):
    t = html.escape(title.strip())
    # Permitimos saltos y lists básicos ya en el CSV (no escaparlos).
    msg = f"<b>{t}</b>\n\n{body.strip()}"
    if cta:
        msg += f"\n\n<a href='{cta}'>Acceder</a>"
    return msg

def send_message(html_msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    r = requests.post(url, json={"chat_id": CHAT_ID, "text": html_msg, "parse_mode":"HTML", "disable_web_page_preview": False})
    r.raise_for_status()

def main():
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ Falta TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID"); return
    if not DATA.exists():
        print("❌ Falta data/telegram_queue.csv"); return

    rows = list(csv.DictReader(open(DATA, encoding="utf-8")))
    idx, r = next_pending(rows)
    if idx is None:
        print("⚠️ No hay mensajes pendientes."); return

    title, body, cta = r["title"], r["body"], r.get("cta","")
    if not quality_ok(title, body):
        print("⚠️ Mensaje rechazado por calidad. Marcado como draft.")
        rows[idx]["status"] = "draft"
    else:
        msg = build_html(title, body, cta)
        send_message(msg)
        rows[idx]["status"] = "done"
        print(f"✅ Enviado a Telegram: {title}")

    with open(DATA, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader(); w.writerows(rows)

if __name__ == "__main__":
    main()
