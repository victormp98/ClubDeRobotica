from app.extensions import db
from app.models.page import Page

DEFAULT_PAGES = [
    {
        'slug': 'about',
        'titulo': 'Sobre el Club',
        'contenido': (
            '<h2>Bienvenidos al Club de Robótica</h2>'
            '<p>Somos un grupo de estudiantes apasionados por la tecnología, la programación y la robótica. '
            'Nuestro objetivo es fomentar el aprendizaje colaborativo y la innovación tecnológica dentro y fuera del aula.</p>'
            '<h3>Nuestra Misión</h3>'
            '<p>Desarrollar las habilidades técnicas y creativas de nuestros miembros a través de proyectos reales, '
            'competencias nacionales e internacionales como la <strong>World Robot Olympiad (WRO)</strong>, '
            'y talleres especializados en robótica, programación e inteligencia artificial.</p>'
            '<h3>¿Qué hacemos?</h3>'
            '<ul>'
            '<li>Construimos y programamos robots autónomos.</li>'
            '<li>Participamos en competencias regionales y nacionales.</li>'
            '<li>Desarrollamos proyectos de innovación tecnológica.</li>'
            '<li>Organizamos talleres y sesiones de entrenamiento semanales.</li>'
            '</ul>'
            '<p>Si te apasiona la tecnología y quieres ser parte de algo grande, '
            '¡únete al Club de Robótica!</p>'
        )
    },
    {
        'slug': 'terminos',
        'titulo': 'Términos y Condiciones',
        'contenido': (
            '<h2>Términos y Condiciones de Uso</h2>'
            '<p>Al registrarte y utilizar esta plataforma del Club de Robótica, aceptas los siguientes términos:</p>'
            '<h3>1. Uso de la Plataforma</h3>'
            '<p>Esta plataforma es de uso exclusivo para miembros activos y administradores del Club de Robótica. '
            'El acceso es controlado y requiere aprobación del administrador.</p>'
            '<h3>2. Responsabilidad del Usuario</h3>'
            '<p>Cada usuario es responsable de mantener la confidencialidad de sus credenciales de acceso '
            'y de todas las actividades que se realicen con su cuenta.</p>'
            '<h3>3. Contenido</h3>'
            '<p>Los usuarios se comprometen a no publicar contenido inapropiado, ofensivo o que viole derechos de terceros. '
            'El club se reserva el derecho de eliminar contenido que no cumpla con estas normas.</p>'
            '<h3>4. Privacidad</h3>'
            '<p>La información personal de los miembros será utilizada únicamente para fines internos del club '
            'y no será compartida con terceros sin consentimiento explícito.</p>'
            '<h3>5. Modificaciones</h3>'
            '<p>El Club de Robótica se reserva el derecho de modificar estos términos en cualquier momento. '
            'Los cambios serán notificados a través de la plataforma.</p>'
            '<p><em>Última actualización: 2026</em></p>'
        )
    }
]

def auto_seed_pages(app):
    """
    Crea las páginas estáticas por defecto si no existen en la BD.
    Esencial para el modo portable/offline donde la BD empieza vacía.
    """
    with app.app_context():
        existing_slugs = set(p.slug for p in Page.query.all())
        added_count = 0

        for page_data in DEFAULT_PAGES:
            if page_data['slug'] not in existing_slugs:
                nueva_page = Page(
                    slug=page_data['slug'],
                    titulo=page_data['titulo'],
                    contenido=page_data['contenido']
                )
                db.session.add(nueva_page)
                added_count += 1

        if added_count > 0:
            db.session.commit()
            app.logger.info(f"[*] auto_seed_pages: Se crearon {added_count} páginas estáticas por defecto.")
        else:
            app.logger.info("[~] auto_seed_pages: Todas las páginas estáticas ya existen.")
