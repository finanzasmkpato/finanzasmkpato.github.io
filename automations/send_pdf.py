from pathlib import Path
import os, yaml, io, requests
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, ListFlowable, ListItem
from reportlab.lib.enums import TA_CENTER

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "pdf_queue.yml"
ASSETS = ROOT / "assets" / "DckFinalSinfondo.png"

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")  # canal destino

GREEN = colors.Color(16/255,185/255,129/255)    # #10B981
GOLD  = colors.Color(212/255,175/255,55/255)    # #D4AF37
BG    = colors.Color(11/255,18/255,33/255)      # #0b1221
TEXT  = colors.whitesmoke

def draw_header(c, title, subtitle):
    c.setFillColor(BG); c.rect(0, 0, 100*cm, 100*cm, stroke=0, fill=1)
    if ASSETS.exists():
        c.drawImage(str(ASSETS), 2*cm, 26*cm, width=2.2*cm, preserveAspectRatio=True, mask='auto')
    c.setFillColor(TEXT); c.setFont("Helvetica-Bold", 20)
    c.drawString(5*cm, 28.2*cm, title[:60])
    c.setFillColor(GOLD); c.setFont("Helvetica", 12)
    c.drawString(5*cm, 27.4*cm, subtitle[:90])

def build_pdf(meta, sections, outpath):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=2.0*cm, rightMargin=2.0*cm, topMargin=3.2*cm, bottomMargin=2.0*cm)
    styles = {
        "h2": ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=16, textColor=GOLD, spaceAfter=8),
        "p": ParagraphStyle("p", fontName="Helvetica", fontSize=11, leading=16, textColor=TEXT),
        "center": ParagraphStyle("center", fontName="Helvetica", fontSize=10, textColor=colors.grey, alignment=TA_CENTER),
    }
    story = []
    story.append(Spacer(1, 1*cm))
    for sec in sections:
        if "title" in sec: story.append(Paragraph(sec["title"], styles["h2"]))
        if "text" in sec:  story.append(Paragraph(sec["text"].replace("\n","<br/>"), styles["p"]))
        if "bullets" in sec:
            items = [ListItem(Paragraph(b, styles["p"]), leftIndent=10) for b in sec["bullets"]]
            story.append(ListFlowable(items, bulletType='bullet', bulletColor=GREEN))
        story.append(Spacer(1, 0.4*cm))
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph(meta.get("footer",""), styles["center"]))
    def on_page(c, d): draw_header(c, meta["title"], meta.get("subtitle",""))
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    pdf_bytes = buf.getvalue(); buf.close()
    Path(outpath).write_bytes(pdf_bytes)
    return outpath

def send_pdf(path, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    with open(path, "rb") as f:
        r = requests.post(url, data={"chat_id": CHAT_ID, "caption": caption}, files={"document": f})
    r.raise_for_status()

def main():
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ Falta TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID"); return
    if not DATA.exists():
        print("❌ Falta data/pdf_queue.yml"); return

    queue = yaml.safe_load(DATA.read_text(encoding="utf-8"))
    # Primer pendiente
    job = next((j for j in queue if j.get("status","pending")=="pending"), None)
    if not job:
        print("⚠️ No hay PDFs pendientes."); return

    meta = job["meta"]; sections = job["sections"]
    out = ROOT / "downloads" / (meta["slug"] + ".pdf")
    out.parent.mkdir(exist_ok=True)
    build_pdf(meta, sections, out)
    caption = meta.get("caption","Recurso MkPato")
    send_pdf(out, caption)
    job["status"]="done"
    DATA.write_text(yaml.safe_dump(queue, allow_unicode=True), encoding="utf-8")
    print(f"✅ PDF enviado: {out}")

if __name__ == "__main__":
    main()
