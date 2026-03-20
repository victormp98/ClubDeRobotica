import re

file_path = r'c:\Users\victo\OneDrive\Desktop\Proyectos\CLUBDEROBOTICA - App\ClubDeRobotica\app\templates\wro.html'

with open(file_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Remover botones de engranaje para JSON modals
html = re.sub(r'<button onclick="openJsonModal[^>]+>⚙️</button>\n?\s*', '', html)

# 2. Corregir renderizado de Categorías
html = html.replace("cat.imagen", "cat.imagen_path if '/' in (cat.imagen_path or '') else 'uploads/torneo_categorias/' ~ cat.imagen_path")

# 3. Corregir renderizado de Recuadros
html = html.replace('item.icon', 'item.icono')
html = html.replace('item.label', 'item.etiqueta')
html = html.replace('item.value', 'item.valor')

# 4. Corregir renderizado de Fechas (remover fallback problemático y usar la lista de modelos)
# Fallback que usa tuplas y rompe la orientación a objetos
fallback_fechas_regex = r'\{%\s*set fechas = fechas_torneo if fechas_torneo else \[[^\]]*\]\s*%\}'
html = re.sub(fallback_fechas_regex, '{% set fechas = fechas_torneo %}', html, flags=re.DOTALL)
html = html.replace('{% for fecha, nombre, desc, status_class, status_label in fechas %}', '{% for f in fechas %}')
html = html.replace('{{ fecha }}', '{{ f.fecha }}')
html = html.replace('{{ nombre }}', '{{ f.nombre }}')
html = html.replace('{{ desc }}', '{{ f.descripcion }}')
html = html.replace('{{ status_class }}', '{{ f.estado_clase }}')
html = html.replace('{{ status_label }}', '{{ f.estado_etiqueta }}')

# 5. Requisitos
html = html.replace('{{ req }}', '{{ req.texto if str(req) != req else req }}')

# 6. Proyectos
html = html.replace('item.imagen', "item.imagen_path if '/' in (item.imagen_path or '') else 'uploads/torneo_proyectos/' ~ item.imagen_path")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(html)
print("Adaptación de atributos en wro.html exitosa.")
