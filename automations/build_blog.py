from pathlib import Path
import csv, os, datetime, re, random, textwrap

# === CONFIGURACIÓN ===
ROOT = Path(__file__).resolve().parents[1]
BLOG = ROOT / "blog"
DATA = ROOT / "data" / "queue.csv"

PRODUCT_URL = os.getenv("PRODUCT_URL", "https://go.hotmart.com/F102330634N?dp=1")
DATE_TODAY = datetime.date.today().isoformat()


# === GENERADOR DE ARTÍCULOS ===
def generate_long_article(title: str, summary: str, tags: str) -> str:
    """
    Genera un artículo largo (~800 palabras) con estructura profesional, sin usar IA externa.
    """

    intros = [
        f"{summary.capitalize()}. En un mundo lleno de distracciones, aplicar {title.lower()} se ha vuelto clave para quienes buscan resultados reales.",
        f"¿Cuántas veces has sentido que trabajas mucho pero avanzas poco? {title} puede ser la diferencia entre el caos y la claridad.",
    ]

    h2_sections = [
        ("🧭 Por qué este principio funciona", 
         f"El enfoque de {title.lower()} no es magia: es gestión consciente. Cuando diriges tu energía a lo esencial, el progreso se acelera sin hacer más."),
        ("⚙️ Cómo aplicarlo paso a paso", 
         "Empieza pequeño: elige una tarea, elimina lo que no aporta y repite. La consistencia vence a la intensidad."),
        ("🚫 Errores que debes evitar", 
         "El más común es confundir movimiento con progreso. No necesitas más herramientas, sino más intención."),
        ("💡 Ejemplo real", 
         "Ana, diseñadora freelance, dedicaba horas a responder correos. Al aplicar este método, bloqueó 30 minutos diarios y liberó 2 horas para trabajo profundo."),
        ("🔚 Conclusión", 
         f"{title} no es una moda: es un sistema para enfocar tu energía y avanzar con claridad.")
    ]

    tips = [
        "Crea una lista de *no-tareas*: cosas que ya no harás.",
        "Define un bloque diario sin interrupciones.",
        "Evalúa cada noche en qué invertiste tu energía.",
        "Automatiza pequeñas decisiones para liberar enfoque.",
    ]

    story_snippets = [
        "Pedro, emprendedor digital, descubrió que solo el 20 % de sus tareas generaban el 80 % de sus ingresos.",
        "Laura, estudiante y madre, usó la técnica 1-1-1 para equilibrar estudio, trabajo y descanso.",
        "Un equipo remoto redujo sus reuniones un 40 % al adoptar este método, ganando claridad y motivación.",
    ]

    body = f"<p>{random.choice(intros)}</p>"

    for h2, paragraph in h2_sections:
        body += f"<h2>{h2}</h2><p>{paragraph}</p>"
        if "Cómo aplicarlo" in h2:
            body += "<ul>" + "".join([f"<li>{t}</li>" for t in tips]) + "</ul>"
        if "Ejemplo real" in h2:
            body += f"<p>{random.choice(story_snippets)}</p>"

    cierre = random.choice([
        f"<p>En resumen, {title} te entrena para pensar con claridad y actuar con propósito.</p>",
        f"<p>Empieza hoy: no esperes el momento perfecto, créalo aplicando {title.lower()} desde ahora.</p>",
    ])

    return body + cierre



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
    :root {{
      --bg:#0b1221; --text:#e6edf7; --muted:#8b98b9; --brand:#10b981; --brand-2:#34d399; --card:#111b2c; --radius:16px;
    }}
    body {{
      background:var(--bg); color:var(--text);
      font-family:Inter,system-ui,sans-serif; margin:0; line-height:1.7;
    }}
    article {{
      max-width:760px; margin:0 auto; padding:60px 24px;
    }}
    h1 {{ text-align:center; font-size:36px; font-weight:800; margin:20px 0; }}
    h2 {{ color:var(--brand); margin-top:30px; }}
    ul {{ margin-left:20px; }}
    a.cta {{
      display:block; width:fit-content; margin:40px auto;
      background:linear-gradient(135deg,var(--brand),var(--brand-2));
      color:#07131a; padding:14px 28px; border-radius:16px;
      font-weight:700; text-decoration:none; box-shadow:0 8px 25px rgba(16,185,129,.25);
    }}
    footer {{
      text-align:center; margin:60px 0; color:var(--muted); font-size:14px;
    }}
  </style>
</head>
<body>
  <article>
    <p class='date'>{date}</p>
    <h1>{title}</h1>
    <div class='highlight'><strong>Mini-resumen:</strong> {summary}</div>
    {body}
    <div style='background:#111b2c;padding:20px;border-radius:16px;margin-top:40px;'>
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
  </article>
  <footer><p><a href='/blog/'>← Volver al archivo</a></p></footer>
</body>
</html>"""


def render_post_html(title, body, url, tags, product_url, summary):
    desc = (summary or body)[:150].replace('"', "").replace("<", "").replace(">", "")
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
        body=body,  # ✅ sin replace ni comillas
        product=product_url,
        tags=tags,
        cta=chosen_cta,
    )



# === PROCESO PRINCIPAL ===
def main():
    if not DATA.exists():
        print("❌ No se encontró data/queue.csv")
        return

    with open(DATA, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        print("⚠️ CSV vacío.")
        return

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

    BLOG.mkdir(exist_ok=True)
    slug = "-".join(re.findall(r"[a-z0-9áéíóúüñ]+", title.lower()))
    out = BLOG / f"{slug}.html"
    out.write_text(render_post_html(title, article_body, url, tags, PRODUCT_URL, summary), encoding="utf-8")

    rows[idx]["status"] = "done"
    with open(DATA, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ Publicado: {title} → {out}")


if __name__ == "__main__":
    main()
