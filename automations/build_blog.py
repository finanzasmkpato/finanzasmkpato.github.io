# build_blog.py — versión PRO MkPato
from pathlib import Path
import csv
import datetime
import os

ROOT = Path(__file__).resolve().parents[1]
BLOG = ROOT / "blog"
DATA = ROOT / "data" / "queue.csv"
PRODUCT_URL = os.getenv("PRODUCT_URL", "https://go.hotmart.com/F102330634N?dp=1")
AFFILIATE_TAG = os.getenv("AFFILIATE_TAG", "")
DATE_TODAY = datetime.date.today().isoformat()


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
      max-width: 720px;
      margin: 0 auto;
      padding: 60px 24px;
    }}
    h1 {{
      text-align: center;
      font-size: 34px;
      font-weight: 800;
      margin-bottom: 16px;
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
      margin: 30px auto 10px;
      width: 80px;
      height: auto;
      opacity: 0.95;
    }}
    a.cta {{
      display: block;
      width: fit-content;
      margin: 30px auto;
      text-align: center;
      background: linear-gradient(135deg, var(--brand), var(--brand-2));
      color: #07131a;
      padding: 14px 24px;
      border-radius: var(--radius);
      font-weight: 700;
      text-decoration: none;
      box-shadow: 0 6px 25px rgba(16,185,129,.25);
      transition: all .2s ease-in-out;
    }}
    a.cta:hover {{
      transform: translateY(-2px);
    }}
    hr {{
      border: none;
      border-top: 1px solid #1f2937;
      margin: 30px 0;
    }}
    p.muted {{
      color: var(--muted);
      font-size: 14px;
    }}
    footer {{
      text-align: center;
      margin-bottom: 40px;
      color: var(--muted);
    }}
    footer a {{
      color: var(--brand);
      text-decoration: none;
    }}
    a.inline {{
      color: var(--brand);
      text-decoration: underline;
    }}
  </style>
</head>
<body>
  <img src='/assets/DckFinalSinfondo.png' alt='MkPato logo' class='logo'>
  <article>
    <p class='date'>{date}</p>
    <h1>{title}</h1>
    {image}
    <p>{body}</p>
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





def render_post_html(title, body, url, image, tags, product_url, affiliate_tag):
    if affiliate_tag and url and "?" not in url:
        url = f"{url}?tag={affiliate_tag}"
    img = f"<img src='{image}' alt='' style='max-width:100%;border-radius:14px;margin-bottom:20px;'>" if image else ""
    link = f"<p><a href='{url}' target='_blank' rel='noopener'>{url}</a></p>" if url else ""
    return TEMPLATE_POST.format(
        title=title,
        desc=body[:150].replace('"', ''),
        date=DATE_TODAY,
        image=img,
        body=body,
        product=product_url or "#",
        link=link,
        tags=tags,
    )


def update_blog_index():
    """Crea índice visual del blog"""
    items = []
    for p in sorted(BLOG.glob("*.html"), key=lambda x: x.stat().st_mtime, reverse=True):
        if p.name == "index.html":
            continue
        title = p.stem.replace("-", " ").title()
        date = DATE_TODAY
        items.append(f"""
        <div class='post-card'>
          <h2><a href='/blog/{p.name}'>{title}</a></h2>
          <p>{date}</p>
          <a href='/blog/{p.name}'>Leer más →</a>
        </div>
        """)
    html = (ROOT / "blog" / "index.html").read_text(encoding="utf-8")
    html = html.replace("<!-- BLOG_POSTS -->", "\n".join(items))
    (ROOT / "blog" / "index.html").write_text(html, encoding="utf-8")
    return items


def update_home_latest():
    """Inserta los 4 posts más recientes en el index principal"""
    links = []
    for p in sorted(BLOG.glob("*.html"), key=lambda x: x.stat().st_mtime, reverse=True):
        if p.name == "index.html":
            continue
        title = p.stem.replace("-", " ").title()
        links.append(f"<div><a href='/blog/{p.name}'>{title}</a></div>")
    links = links[:4]
    home = (ROOT / "index.html").read_text(encoding="utf-8")
    home = home.replace("<!-- LATEST_POSTS -->", "<div class='postlist'>" + "".join(links) + "</div>")
    (ROOT / "index.html").write_text(home, encoding="utf-8")


def main():
    """Genera un post diario y actualiza el blog"""
    if not DATA.exists():
        print("queue.csv no encontrado.")
        return

    with open(DATA, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    for row in rows:
        if row["status"] == "pending":
            title = row["title"]
            body = row["body"]
            url = row["url"]
            image = row["image"]
            tags = row["tags"]
            filename = "-".join(title.lower().split()) + ".html"
            outpath = BLOG / filename
            html = render_post_html(title, body, url, image, tags, PRODUCT_URL, AFFILIATE_TAG)
            outpath.write_text(html, encoding="utf-8")
            row["status"] = "done"
            break

    with open(DATA, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    update_blog_index()
    update_home_latest()
    print("Blog actualizado correctamente.")


if __name__ == "__main__":
    main()
