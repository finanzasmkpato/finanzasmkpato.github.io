from pathlib import Path
import csv
import datetime
import os

# Rutas
ROOT = Path(__file__).resolve().parents[1]
BLOG = ROOT / "blog"
DATA = ROOT / "data" / "queue.csv"
PRODUCT_URL = os.getenv("PRODUCT_URL", "https://go.hotmart.com/F102330634N?dp=1")
AFFILIATE_TAG = os.getenv("AFFILIATE_TAG", "")
DATE_TODAY = datetime.date.today().isoformat()

# ---------------- TEMPLATE ----------------
TEMPLATE_POST = """<!doctype html>
<html lang='es'>
<head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width,initial-scale=1'>
  <title>{title} · MkPato</title>
  <meta name='description' content='{desc}'>
  <link href='https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap' rel='stylesheet'>
  <style>
    :root {{
      --bg: #0b1221;
      --text: #e6edf7;
      --muted: #8b98b9;
      --brand: #10b981;
      --brand-2: #34d399;
      --card: #111b2c;
      --radius: 16px;
      font-family: 'Inter', system-ui, sans-serif;
    }}
    body {{
      background: var(--bg);
      color: var(--text);
      font-family: 'Inter', sans-serif;
      margin: 0;
      padding: 0;
      line-height: 1.7;
    }}
    article {{
      max-width: 760px;
      margin: 0 auto;
      padding: 60px 24px;
    }}
    h1 {{
      text-align: center;
      font-size: 36px;
      font-weight: 800;
      margin-bottom: 20px;
      color: var(--text);
    }}
    p.date {{
      text-align: center;
      color: var(--muted);
      font-size: 14px;
      margin-bottom: 30px;
    }}
    img.logo {{
      display: block;
      margin: 40px auto 10px;
      width: 80px;
      height: auto;
      opacity: 0.95;
    }}
    .highlight {{
      background: var(--card);
      padding: 18px 20px;
      border-left: 4px solid var(--brand);
      border-radius: var(--radius);
      margin: 30px 0;
      font-size: 15px;
    }}
    .learn-box {{
      background: var(--card);
      border-radius: var(--radius);
      padding: 20px;
      margin-top: 40px;
    }}
    .learn-box h3 {{
      margin-top: 0;
      color: var(--brand);
      font-weight: 700;
    }}
    .learn-box ul {{
      margin: 10px 0 0 20px;
      padding: 0;
      color: var(--text);
    }}
    a.cta {{
      display: block;
      width: fit-content;
      margin: 40px auto;
      text-align: center;
      background: linear-gradient(135deg, var(--brand), var(--brand-2));
      color: #07131a;
      padding: 16px 28px;
      border-radius: var(--radius);
      font-weight: 700;
      text-decoration: none;
      box-shadow: 0 8px 25px rgba(16,185,129,.25);
      transition: all .2s ease-in-out;
    }}
    a.cta:hover {{
      transform: translateY(-2px);
    }}
    hr {{
      border: none;
      border-top: 1px solid #1f2937;
      margin: 40px 0;
    }}
    footer {{
      text-align: center;
      margin: 60px 0;
      color: var(--muted);
      font-size: 14px;
    }}
    footer a {{
      color: var(--brand);
      text-decoration: none;
    }}
  </style>
</head>
<body>
  <img src='/assets/DckFinalSinfondo.png' alt='MkPato logo' class='logo'>
  <article>
    <p class='date'>{date}</p>
    <h1>{title}</h1>
    {image}
    <div class='highlight'>
      <strong>Mini-resumen:</strong> {summary}
    </div>
    <p>{body}</p>
    <div class='learn-box'>
      <h3>💡 3 aprendizajes clave</h3>
      <ul>
        <li>Aplica el sistema, no la teoría.</li>
        <li>Registra tus resultados diarios en 2 minutos.</li>
        <li>Conviértelo en hábito: mejora 1% cada día.</li>
      </ul>
    </div>
    <a class='cta' href='{product}' target='_blank' rel='noopener'>Acceder al Pack PRO</a>
    {link}
    <hr>
    <p class='muted'>Etiquetas: {tags}</p>
  </article>
  <footer>
    <p><a href='/blog/'>← Volver al archivo</a></p>
  </footer>
</body>
</html>"""


def render_post_html(title, body, url, image, tags, product_url):
    summary = (body[:150] + "...") if len(body) > 150 else body
    img = f"<img src='{image}' alt='' class='hero'>" if image else ""
    link = f"<p><a href='{url}' target='_blank' rel='noopener' style='color:#10b981'>{url}</a></p>" if url else ""
    return TEMPLATE_POST.format(
        title=title,
        desc=body[:150].replace('"', ''),
        date=DATE_TODAY,
        image=img,
        body=body,
        product=product_url,
        link=link,
        tags=tags,
        summary=summary
    )


def main():
    if not DATA.exists():
        print("❌ No se encontró data/queue.csv")
        return

    with open(DATA, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    for row in rows:
        if row.get("status", "pending") == "pending":
            title = row["title"]
            body = row["body"]
            url = row.get("url", "")
            image = row.get("image", "")
            tags = row.get("tags", "")
            filename = "-".join(title.lower().split()) + ".html"
            outpath = BLOG / filename
            html = render_post_html(title, body, url, image, tags, PRODUCT_URL)
            outpath.write_text(html, encoding="utf-8")
            row["status"] = "done"
            print(f"✅ Publicado: {title}")
            break
    else:
        print("⚠️ No hay entradas pendientes en la cola.")

    with open(DATA, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
