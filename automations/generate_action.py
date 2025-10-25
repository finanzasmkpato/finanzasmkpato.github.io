import os
import yaml
from datetime import datetime
from weasyprint import HTML, CSS

# === CONFIGURACIÓN ===
data_path = "data/actions.yml"
pdf_path = "site/action_report.pdf"

# Crear carpetas necesarias
os.makedirs("data", exist_ok=True)
os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

# === Cargar o crear archivo YAML ===
if not os.path.exists(data_path):
    print(f"⚠️ Archivo {data_path} no encontrado. Creando uno vacío...")
    with open(data_path, "w", encoding="utf-8") as f:
        f.write("systems: []")

with open(data_path, "r", encoding="utf-8") as f:
    try:
        data = yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        print(f"⚠️ Error leyendo {data_path}: {e}")
        data = {}

systems = data.get("systems", [])

# === Construir contenido HTML dinámico ===
system_blocks = ""
if systems:
    for i, s in enumerate(systems, start=1):
        title = s.get("title", f"Acción #{i}")
        subtitle = s.get("subtitle", "")
        objective = s.get("objective", "")
        steps = s.get("steps", [])
        rule = s.get("rule", "")
        prompt = s.get("prompt", "")
        metric = s.get("metric", "")
        cta = s.get("cta", "")

        steps_html = "".join([f"<li>{step}</li>" for step in steps])

        system_blocks += f"""
        <div class="block">
            <h2>{title}</h2>
            <p class="subtitle">{subtitle}</p>
            <p><b>🎯 Objetivo:</b> {objective}</p>
            <ul>{steps_html}</ul>
            <p class="rule">💬 <b>Regla:</b> {rule}</p>
            <p><b>🧠 Prompt sugerido:</b> <i>{prompt}</i></p>
            <p><b>📊 Métrica:</b> {metric}</p>
            <p class="cta">➡️ {cta}</p>
        </div>
        """
else:
    system_blocks = "<p>No hay acciones definidas.</p>"

# === HTML final ===
html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Informe de Acciones MkPato</title>
<style>
  body {{
    font-family: 'Inter', sans-serif;
    margin: 40px;
    color: #111827;
    background-color: #ffffff;
  }}
  h1 {{
    color: #065f46;
    text-align: center;
  }}
  h2 {{
    color: #047857;
    margin-top: 30px;
  }}
  .subtitle {{
    font-style: italic;
    color: #6b7280;
    margin-bottom: 10px;
  }}
  ul {{
    margin-left: 20px;
    margin-bottom: 10px;
  }}
  .rule {{
    background-color: #fef9c3;
    padding: 10px;
    border-radius: 8px;
  }}
  .cta {{
    color: #92400e;
    font-weight: bold;
    margin-top: 5px;
  }}
  .footer {{
    text-align: center;
    font-size: 12px;
    color: #6b7280;
    margin-top: 40px;
  }}
  .block {{
    background-color: #f9fafb;
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 20px;
    borde

