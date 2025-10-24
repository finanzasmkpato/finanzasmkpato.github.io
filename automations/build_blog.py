# build_blog.py — MkPato PRO + IA (HuggingFace Inference API)
from pathlib import Path
import csv, os, datetime, re
from huggingface_hub import InferenceClient

ROOT = Path(__file__).resolve().parents[1]
BLOG = ROOT / "blog"
DATA = ROOT / "data" / "queue.csv"

PRODUCT_URL = os.getenv("PRODUCT_URL", "https://go.hotmart.com/F102330634N?dp=1")
AFFILIATE_TAG = os.getenv("AFFILIATE_TAG", "")
HF_API_TOKEN = os.getenv("HF_API_TOKEN", "")
MODEL_ID = os.getenv("HF_MODEL_ID", "mistralai/Mistral-7B-Instruct")  # puedes cambiarlo

DATE_TODAY = datetime.date.today().isoformat()

# ---------- IA ----------
from huggingface_hub import InferenceClient
from huggingface_hub.errors import RepositoryNotFoundError
import requests, os, random

def generate_long_article(title: str, summary: str, tags: str) -> str:
    """
    Genera artículo profesional (~1000 palabras) con estructura completa, tono editorial y SEO-friendly.
    Incluye fallback automático si el modelo falla.
    """

    main_model = os.getenv("HF_MODEL_ID", "mistralai/Mistral-7B-Instruct")
    backup_model = "google/flan-t5-large"
    HF_API_TOKEN = os.getenv("HF_API_TOKEN")

    def infer(model_id, prompt):
        client = InferenceClient(token=HF_API_TOKEN)
        return client.text_generation(
            model=model_id,
            prompt=prompt,
            max_new_tokens=1300,
            temperature=0.75,
            top_p=0.92,
            repetition_penalty=1.1,
            return_full_text=False,
        ).strip()

    # 🔹 Variedad de estilo para rotar automáticamente
    styles = [
        "una guía práctica paso a paso",
        "un artículo de reflexión profunda",
        "una historia inspiradora con moraleja financiera",
        "una mini-lección de productividad real",
        "un análisis con ejemplos reales y consejos aplicables"
    ]
    tone = random.choice(styles)

    # 🔹 Prompt mejorado para redacción PRO
    prompt = f"""
Eres un redactor experto en finanzas personales, productividad y hábitos.

Redacta un artículo en español de unas 1000 palabras titulado "{title}".
Debe estar basado en esta idea: "{summary}".

El texto debe tener una estructura profesional con:
1. Un subtítulo atractivo (H2) bajo el título principal.
2. Una introducción con gancho y contexto real.
3. Secciones claras con subtítulos H3.
4. Listas con viñetas o pasos concretos.
5. Un ejemplo real o mini-historia.
6. Una conclusión potente con CTA implícito a mejorar la claridad financiera o usar el sistema de MkPato.

Tono: claro, cercano, profesional, con autoridad amable.
Evita relleno y frases vacías. Que aporte valor real y acción inmediata.

Incluye etiquetas y menciona conceptos de {tags or "finanzas, productividad, claridad, hábitos"}.
"""

    def cleanup(text: str) -> str:
        text = text.strip()
        if not text:
            return expand_fallback(title, summary, tags)


    client = InferenceClient(token=HF_API_TOKEN)
    prompt = f"""Eres un escritor experto en productividad y finanzas personales.
Escribe un artículo de 500 palabras en español, claro y accionable, sobre: "{title}".
Contexto/resumen: "{summary or title}".
Estructura: 1) introducción breve con gancho, 2) desarrollo con 3–4 ideas prácticas,
3) ejemplo real o mini-historia, 4) cierre con consejo accionable.
Tono: profesional, directo, sin paja. Evita listas vacías; usa párrafos consistentes.
Relaciona con: {tags or "productividad, finanzas, claridad mental"}.
"""
    # Generación
    out = client.text_generation(
        model=MODEL_ID,
        prompt=prompt,
        max_new_tokens=700,  # ~500 palabras
        temperature=0.8,
        top_p=0.95,
        repetition_penalty=1.05,
        return_full_text=False,
    )
    text = out.strip()
    return cleanup(text)

def expand_fallback(title: str, summary: str, tags: str) -> str:
    """Generador offline (por si falla la API). ~450–550 palabras."""
    s = summary or title
    p1 = f"{s.capitalize()}. Esta idea resume un principio simple: la claridad dirige la acción."
    p2 = f"En {tags or 'productividad'}, muchas personas saltan de tarea en tarea sin prioridad. {title} reduce el ruido y enfoca energía."
    p3 = f"Cómo aplicarlo hoy: define 1 objetivo, 1 tarea clave y 1 freno que vas a eliminar. Escríbelo y blíndalo en tu agenda."
    p4 = "Errores comunes: confundir movimiento con progreso, acumular herramientas sin hábitos y no medir resultados."
    p5 = "Mini-historia: un lector bloqueó 20 minutos al día para su 1 tarea clave. En 3 semanas terminó un proyecto aparcado 6 meses."
    p6 = "Cierre: convierte esto en un estándar. Evalúa al final del día si cumpliste tu 1-1-1. Ajusta, itera y vuelve a empezar mañana."
    return "\n\n".join([p1,p2,p3,p4,p5,p6])

def cleanup(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text

# ---------- PLANTILLA VISUAL DEL POST ----------
TEMPLATE_POST = """<!doctype html>
<html lang='es'>
<head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width,initial-scale=1'>
  <title>{title} · MkPato</title>
  <meta name='description' content='{desc}'>
  <link href='https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap' rel='stylesheet'>
  <style>
    :root {{ --bg:#0b1221; --text:#e6edf7; --muted:#8b98b9; --brand:#10b981; --brand-2:#34d399; --card:#111b2c; --radius:16px; }}
    body {{ background:var(--bg); color:var(--text); font-family:Inter,system-ui,sans-serif; margin:0; line-height:1.7; }}
    article {{ max-width:760px; margin:0 auto; padding:60px 24px; }}
    h1 {{ text-align:center; font-size:36px; font-weight:800; margin:20px 0; }}
    p.date {{ text-align:center; color:var(--muted); font-size:14px; margin-top:10px; }}
    img.logo {{ display:block; margin:40px auto 10px; width:80px; height:auto; opacity:.95; }}
    .highlight {{ background:var(--card); padding:18px 20px; border-left:4px solid var(--brand); border-radius:16px; margin:30px 0; font-size:15px; }}
    .learn-box {{ background:var(--card); border-radius:16px; padding:20px; margin-top:40px; }}
    .learn-box h3 {{ margin-top:0; color:var(--brand); font-weight:700; }}
    .learn-box ul {{ margin:10px 0 0 20px; padding:0; }}
    a.cta {{ display:block; width:fit-content; margin:40px auto; text-align:center;
             background:linear-gradient(135deg,var(--brand),var(--brand-2)); color:#07131a; padding:16px 28px;
             border-radius:16px; font-weight:700; text-decoration:none; box-shadow:0 8px 25px rgba(16,185,129,.25); }}
    hr {{ border:none; border-top:1px solid #1f2937; margin:40px 0; }}
    footer {{ text-align:center; margin:60px 0; color:var(--muted); font-size:14px; }}
    footer a {{ color:var(--brand); text-decoration:none; }}
  </style>
</head>
<body>
  <img src='/assets/DckFinalSinfondo.png' alt='MkPato logo' class='logo'>
  <article>
    <p class='date'>{date}</p>
    <h1>{title}</h1>
    <div class='highlight'><strong>Mini-resumen:</strong> {summary}</div>
    <p>{body}</p>
    <div class='learn-box'>
      <h3>💡 3 aprendizajes clave</h3>
      <ul>
        <li>Aplica el sistema, no la teoría.</li>
        <li>Registra resultados en 2 minutos al día.</li>
        <li>Itera: mejora un 1 % cada semana.</li>
      </ul>
    </div>
    <a class='cta' href='{product}' target='_blank' rel='noopener'>Acceder al Pack PRO</a>
    {link}
    <hr>
    <p class='muted'>Etiquetas: {tags}</p>
  </article>
  <footer><p><a href='/blog/'>← Volver al archivo</a></p></footer>
</body>
</html>"""

def render_post_html(title, body, url, tags, product_url, summary):
    link = f"<p><a href='{url}' target='_blank' rel='noopener' style='color:#10b981'>{url}</a></p>" if url else ""
    desc = (summary or body)[:150].replace('"','')
    return TEMPLATE_POST.format(
        title=title, desc=desc, date=DATE_TODAY, summary=summary or "",
        body=body.replace("\n", "<br><br>"), product=product_url, link=link, tags=tags
    )

def update_blog_index():
    items=[]
    for p in sorted(BLOG.glob("*.html"), key=lambda x:x.stat().st_mtime, reverse=True):
        if p.name=="index.html": continue
        t=p.stem.replace("-"," ").title()
        d=DATE_TODAY
        items.append(f"<div class='post-card'><h2><a href='/blog/{p.name}'>{t}</a></h2><p>{d}</p><a href='/blog/{p.name}'>Leer más →</a></div>")
    idx=(ROOT/"blog/index.html").read_text(encoding="utf-8")
    idx=idx.replace("<!-- BLOG_POSTS -->","\n".join(items))
    (ROOT/"blog/index.html").write_text(idx,encoding="utf-8")

def update_home_latest():
    links=[]
    for p in sorted(BLOG.glob('*.html'), key=lambda x:x.stat().st_mtime, reverse=True):
        if p.name=="index.html": continue
        t=p.stem.replace("-"," ").title()
        links.append(f"<div><a href='/blog/{p.name}'>{t}</a></div>")
    links=links[:4]
    home=(ROOT/"index.html").read_text(encoding="utf-8")
    home=home.replace("<!-- LATEST_POSTS -->","<div class='postlist'>"+"".join(links)+"</div>")
    (ROOT/"index.html").write_text(home,encoding="utf-8")

def main():
    rows=list(csv.DictReader(open(DATA,encoding="utf-8")))
    # Buscar primer pending
    idx=None
    for i,r in enumerate(rows):
        if r.get("status","pending").lower()=="pending":
            idx=i; break
    if idx is None:
        print("⚠️ No hay entradas pendientes."); return
    r=rows[idx]
    title=r.get("title","Post").strip()
    url=r.get("url","").strip()
    tags=r.get("tags","").strip()
    summary = r.get("body","").strip()  # tratamos body como “resumen” si existe

    # Generar cuerpo con IA si no hay body largo
    article_body = generate_long_article(title, summary, tags)

    # Escribir post
    BLOG.mkdir(exist_ok=True)
    slug="-".join(re.findall(r"[a-z0-9áéíóúüñ]+", title.lower())).replace(" ", "-")
    out=BLOG/f"{slug}.html"
    out.write_text(render_post_html(title, article_body, url, tags, PRODUCT_URL, summary), encoding="utf-8")

    # Marcar como done
    rows[idx]["status"]="done"
    with open(DATA,"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader(); w.writerows(rows)

    # Actualizar listados
    update_blog_index(); update_home_latest()
    print(f"✅ Publicado con IA: {title} → {out}")

if __name__=="__main__":
    main()
