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


TEMPLATE_POST = """<!doctype html><html lang='es'><head>
<meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>{title}</title>
<meta name='description' content='{desc}'>
<link href='https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap' rel='stylesheet'>
<link rel='stylesheet' href='/assets/style.css'>
</head><body>
<img src='/assets/DckFinalSinfondo.png' alt='MkPato logo' style='width:80px;height:auto;margin:30px auto 10px;display:block;'>
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
</body></html>"""




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
