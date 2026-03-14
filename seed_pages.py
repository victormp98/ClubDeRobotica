"""One-time seeder: inserts initial Page records into the database."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models.page import Page

app = create_app()

PAGES = [
    {
        "slug": "about",
        "titulo": "Acerca de Nosotros",
        "contenido": """<h2 class="text-2xl font-bold mb-4">¿Quiénes Somos?</h2>
<p class="mb-4">Somos el <strong>Club de Robótica de la UNACH</strong>, un espacio donde estudiantes apasionados por la tecnología se unen para aprender, crear y competir en el apasionante mundo de la robótica educativa.</p>
<h2 class="text-2xl font-bold mb-4 mt-6">Nuestra Misión</h2>
<p class="mb-4">Fomentar el pensamiento lógico, creativo y científico en los estudiantes universitarios a través de la programación, electrónica y construcción de robots, preparándolos para los retos tecnológicos del siglo XXI.</p>
<h2 class="text-2xl font-bold mb-4 mt-6">¿Cómo Unirte?</h2>
<p>Regístrate en nuestra página web, llena el formulario de solicitud y espera la aprobación de un coordinador. ¡Las puertas están abiertas para todos los alumnos activos de la universidad!</p>"""
    },
    {
        "slug": "contact",
        "titulo": "Contacto",
        "contenido": """<p class="mb-4">Para cualquier consulta, colaboración o información sobre el Club de Robótica, puedes encontrarnos a través de:</p>
<ul class="list-disc list-inside space-y-2">
  <li><strong>Correo:</strong> clubrobotica@unach.mx</li>
  <li><strong>Facebook:</strong> /ClubRoboticaUNACH</li>
  <li><strong>Ubicación:</strong> Facultad de Ingeniería, UNACH Campus Tuxtla</li>
</ul>"""
    },
    {
        "slug": "terminos",
        "titulo": "Términos y Condiciones",
        "contenido": """<p class="mb-4">Al unirte al Club de Robótica de la UNACH, aceptas conducirte conforme a los siguientes lineamientos:</p>
<ol class="list-decimal list-inside space-y-2">
  <li>Asistir con respeto y actitud colaborativa a las sesiones.</li>
  <li>Cuidar el equipo y material del club para mantenerlo en buen estado.</li>
  <li>Participar activamente en los proyectos y competencias según tu disponibilidad.</li>
  <li>Dar crédito al club en publicaciones relacionadas con los proyectos desarrollados.</li>
</ol>"""
    }
]

with app.app_context():
    count = 0
    for data in PAGES:
        existing = Page.query.filter_by(slug=data["slug"]).first()
        if not existing:
            page = Page(**data)
            db.session.add(page)
            count += 1
            print(f"  [+] Inserted page: {data['slug']}")
        else:
            print(f"  [~] Skipped (already exists): {data['slug']}")
    db.session.commit()
    print(f"\nSeeder complete. {count} new page(s) inserted.")
