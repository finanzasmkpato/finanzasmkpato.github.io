from pathlib import Path
import csv, os, datetime, re, random, requests
from huggingface_hub import InferenceClient
from huggingface_hub.errors import RepositoryNotFoundError

# === CONFIG ===
ROOT = Path(__file__).resolve().parents[1]
BLOG = ROOT / "blog"
DATA = ROOT / "data" / "queue.csv"

PRODUCT_URL = os.getenv("PRODUCT_URL", "https://go.hotmart.com/F102330634N?dp=1")
AFFILIATE_TAG = os.getenv("AFFILIATE_TAG", "")
HF_API_TOKEN = os.getenv("HF_API_TOKEN", "")
DATE_TODAY = datetime.date.today().isoformat()


# === GENERACIÓN DE TEXTO CON IA ===
def generate_long_article(title: str, summary: str, tags: str) -> str:
    """Genera artículo extenso (~1000 palabras) con IA gratuita y fallback automático."""

    main_model = os.getenv("HF_MODEL_ID", "google/flan-t5-xl")
    backup_model = "meta-llama/Llama-3-8b-instruct"

    def infer(model_id, prompt):
        client = InferenceClient(token=HF_API_TOKEN)
        result = client.text_generation(
            model=model_id,
            prompt=prompt,
            max_new_tokens=2000,
            temperature=0.7,
            top_p=0.9,
            repetition_penalty=1.05,
            return_full_text=False,
        )
        return result.strip()

    styles = [
        "una guía práctica paso a paso",
        "una historia inspiradora con moraleja financiera",
        "una reflexión de mentalidad y enfoque",
        "un mini-curso con consejos aplicables",
        "un análisis claro y estructurado de productividad"
    ]
    tone = random.choice(styles)

    prompt = f"""
Eres un redactor experto en finanzas personales y productividad.
Escribe un artículo en español de entre 950 y 1100 palabras titulado "{title}".
Debe basarse en la idea: "{summary}".
Estructura profesional:
1. Introducción con gancho y contexto (sin título “introducción”)
2. 3–5 secciones con subtítulos H2 o H3
3. Consejos o pasos concretos con ejemplos
4. Historia o ejemplo real (mínimo un párrafo)
5. Conclusión con mensaje potente y acción.
Tono: profesional, claro y humano.
Integra naturalmente temas de {tags or "finanzas, productividad, claridad"}.
"""

    def cleanup(text: str) -> str:
        text = text.strip()
        if not text:
            return None
        text = text.replace("**", "").replace("###", "").replace("##", "")
        return text

    try:
        print(f"🧠 Generando artículo con {main_model}...")
        text = cleanup(infer(main_model, prompt))
        if not text or len(text.split()) < 300:
            raise ValueError("Texto demasiado corto o vacío.")
        return text
    except Exception as e:
        print(f"⚠️ Error con {main_model}: {e}")
        print("→ Probando modelo alternativo (Llama-3-8B-Instruct)...")
        try:
            text = cleanup(infer(backup_model, prompt))
            if not text or len(text.split()) < 300:
                raise ValueError("Texto vacío en fallback.")
            return text
        except Exception as e2:
            print(f"⚠️ Fallo total IA: {e2}")
            return expand_fallback(title, summary, tags)


# === BACKUP LOCAL (SIN IA) ===
def expand_fallback(title: str, summary: str, tags: str) -> str:
    """Texto alternativo si la IA falla."""
    s = summary or title
    p1 = f"{s.capitalize()}. Esta idea resume un principio simple: la claridad dirige la acción."
    p2 = f"En {tags or 'productividad'}, muchas personas saltan de tarea en tarea sin prioridad. {title} reduce el ruido y enfoca energía."
    p3 = "Cómo aplicarlo hoy: define 1 objetivo, 1 tarea clave y 1 freno que vas a eliminar. Escríbelo y blíndalo en tu agenda."
    p4 = "Errores comunes: confundir movimiento con progreso, acumular herramientas sin hábitos y no medir resultados."
    p5 = "Mini-historia: un lector bloqueó 20 minutos al día para su 1 tarea clave. En 3 semanas terminó un proyecto aparcado 6 meses."
    p6 = "Cierre: convierte esto en un estándar. Evalúa al final del día si cumpliste tu 1-1-1. Ajusta, itera y vuelve a empezar mañana."
    return "\n\n".join([p1, p2, p3, p4, p5, p6])


# === RENDER HTML ===
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
    a.cta {{ display:block; width:fit-content; margin:40px auto;
             text-align:center; background:linear-gradient(135deg,var(--brand),var(--brand-2));
             color:#07131a; padding:16px 28px; border-radius:16px; font-weight:700;
             text-decoration:none; box-shadow:0 8px 25px rgba(16,185,129,.25); }}
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
    <hr>
    <div style='background:#111b2c;padding:20px;border-radius:16px;'>
      <h3 style='color:#10B981;'>💡 3 aprendizajes clave</h3>
      <ul>
        <li>Aplica el sistema, no la teoría.</li>
        <li>Evalúa tus resultados en 2 minutos diarios.</li>
        <li>Mejora un 1 % cada semana.</li>
      </ul>
    </div>
    <div style='text-align:center;margin-top:40px;'>
      <a class='cta' href='{product}' target='_blank'>Acceder al Pack PRO</a>
      <p style='color:#8b98b9;font-size:14px;margin-top:10px;'>{cta}</p>
    </div>
    <p class='muted'>Etiquetas: {tags}</p>
  </article>
  <footer><p><a href='/blog/'>← Volver al archivo</a></p></footer>
</body>
</html>"""


def render_post_html(title, body, url, tags, product_url, summary):
    desc = (summary or body)[:150].replace('"', '')
    ctas = [
        "Optimiza tus finanzas en 15 minutos al día.",
        "Convierte tus hábitos en libertad financiera.",
        "Domina tu economía y tu enfoque con MkPato.",
        "Descubre cómo multiplicar tu claridad en menos tiempo.",
    ]
    chosen_cta = random.choice(ctas)
    return TEMPLATE_POST.format(
        title=title,
        desc=desc,
        date=DATE_TODAY,
        summary=summary or "",
        body=body.replace("\n", "<br><br>"),
        product=product_url,
        tags=tags,
        cta=chosen_cta,
    )


# === MAIN ===
def main():
    if not DATA.exists():
        print("❌ No se encontró data/queue.csv")
        return

    with open(DATA, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        print("⚠️ CSV vacío.")
        return

    # Buscar primer pendiente
    idx = None
    for i, r in enumerate(rows):
        if r.get("status", "pending").lower() == "pending":
            idx = i
            break
    if idx is None:
        print("⚠️ No hay entradas pendientes.")
        return

    r = rows[idx]
    title = r.get("title", "Post sin título").strip()
    url = r.get("url", "").strip()
    tags = r.get("tags", "").strip()
    summary = r.get("body", "").strip()

    article_body = generate_long_article(title, summary, tags)

    # Protección si la IA devuelve vacío
    if not article_body or not isinstance(article_body, str) or len(article_body.strip()) < 100:
        print("⚠️ Texto IA vacío o corto → usando fallback local.")
        article_body = expand_fallback(title, summary, tags)

    # Escribir post
    BLOG.mkdir(exist_ok=True)
    slug = "-".join(re.findall(r"[a-z0-9áéíóúüñ]+", title.lower()))
    out = BLOG / f"{slug}.html"
    out.write_text(render_post_html(title, article_body, url, tags, PRODUCT_URL, summary), encoding="utf-8")

    # Marcar como publicado
    rows[idx]["status"] = "done"
    with open(DATA, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ Publicado con IA: {title} → {out}")


if __name__ == "__main__":
    main()
