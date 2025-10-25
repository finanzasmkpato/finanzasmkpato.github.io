import os
import yaml
from datetime import datetime
from weasyprint import HTML, CSS

# === CONFIGURACIÓN ===
data_path = "data/actions.yml"
pdf_path = "site/action_report.pdf"

# Crear carpetas si no existen
os.makedirs("data", exist_ok=True)
os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

# === Cargar o crear archivo YAML ===
if not os.path.exists(data_path):
    print(f"⚠️ Archivo {data_path} no encontrado. Creando uno vacío...")
    with open(data_path, "w", encoding="utf-8") as f:
        f.write("actions: []")

with open(data_path, "r", encoding="utf-8") as f:
    try:
        data = yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        print(f"⚠️ Error leyendo {data_path}: {e}")
        data = {}

actions = data.get("actions", [])

# === Construir HTML dinámico ===
rows = ""
if actions:
    for action in actions:
        name = action.get("name", "Sin nombre")
        desc = action.get("description", "Sin descripción")
        status = action.get("status", "Pendiente")
        date = action.get("date", datetime.now().strftime("%d/%m/%Y"))
        rows += f"""
        <tr>
          <td>{name}</td>
          <td>{desc}</td>
          <td>{status}</td>
          <td>{date}</td>
        </tr>
        """
else:
    rows = """<tr><td colspan="4" style="text-align:center;">Sin acciones registradas</td></tr>"""

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
  }}
  h1 {{
    color: #065f46;
    text-align: center;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    margin-top: 25px;
  }}
  th, td {{
    border: 1px solid #d1d5db;
    padding: 10px;
    text-align: left;
    font-size: 14px;
  }}
  th {{
    background-color: #ecfdf5;
    color: #065f46;
  }}
  tr:nth-child(even) {{
    background-color: #f9fafb;
  }}
  .footer {{
    text-align: center;
    font-size: 12px;
    color: #6b7280;
    margin-top: 40px;
  }}
</style>
</head>
<body>
  <h1>📋 Informe de Acciones — Finanzas MkPato</h1>
  <p>Generado automáticamente el <b>{datetime.now().strftime('%d/%m/%Y %H:%M')}</b>.</p>

  <table>
    <thead>
      <tr>
        <th>Acción</th>
        <th>Descripción</th>
        <th>Estado</th>
        <th>Fecha</th>
      </tr>
    </thead>
    <tbody>
      {rows}
    </tbody>
  </table>

  <div class="footer">
    <p>Finanzas MkPato — Sistema autónomo de ingresos © {datetime.now().year}</p>
  </div>
</body>
</html>
"""

# === Generar PDF con WeasyPrint ===
try:
    HTML(string=html).write_pdf(
        pdf_path,
        stylesheets=[CSS(string='@page { size: A4; margin: 1cm }')]
    )
    print(f"✅ PDF generado correctamente: {pdf_path}")
except Exception as e:
    print(f"❌ Error generando el PDF: {e}")
