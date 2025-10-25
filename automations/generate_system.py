import os
from datetime import datetime
from weasyprint import HTML, CSS

# === CONFIGURACIÓN BÁSICA ===
# Nombre del PDF de salida
output_pdf = "site/system_report.pdf"

# Crea carpeta si no existe
os.makedirs(os.path.dirname(output_pdf), exist_ok=True)

# === HTML DEL DOCUMENTO ===
# Puedes reemplazar este bloque con tu HTML real generado dinámicamente
html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Informe del Sistema MkPato</title>
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
  h2 {{
    color: #047857;
    margin-top: 30px;
  }}
  .section {{
    margin-bottom: 25px;
  }}
  .footer {{
    margin-top: 40px;
    text-align: center;
    font-size: 12px;
    color: #6b7280;
  }}
  .highlight {{
    background-color: #ecfdf5;
    padding: 10px;
    border-radius: 8px;
  }}
</style>
</head>
<body>
  <h1>📊 Informe del Sistema — Finanzas MkPato</h1>
  <div class="section">
    <h2>Resumen</h2>
    <p>Este informe fue generado automáticamente el <b>{datetime.now().strftime('%d/%m/%Y %H:%M')}</b>.</p>
    <div class="highlight">
      <p>💼 Estado del sistema: <b>Operativo</b></p>
      <p>⚙️ Automatizaciones activas: <b>3</b></p>
      <p>💰 Ingresos estimados: <b>1.000 €/mes</b></p>
    </div>
  </div>

  <div class="section">
    <h2>Próximos pasos</h2>
    <ul>
      <li>Optimizar embudos de tráfico orgánico.</li>
      <li>Ampliar presencia en Hotmart y Amazon KDP.</li>
      <li>Configurar campaña de crecimiento en Instagram.</li>
    </ul>
  </div>

  <div class="footer">
    <p>Finanzas MkPato — Sistema autónomo de ingresos © {datetime.now().year}</p>
  </div>
</body>
</html>
"""

# === GENERACIÓN DEL PDF ===
print("Generando PDF con WeasyPrint...")

HTML(string=html).write_pdf(
    output_pdf,
    stylesheets=[CSS(string='@page { size: A4; margin: 1cm }')]
)

print(f"✅ PDF generado correctamente: {output_pdf}")
