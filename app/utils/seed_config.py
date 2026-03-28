from app.extensions import db
from app.models.configuracion import Configuracion

DEFAULT_CONFIGS = {
    # == VARIABLES GLOBALES ==
    'drive_virtual_url': ('#', 'Link al Google Drive que ven los miembros en la sección exclusiva.'),
    'IMAGEN_EQUIPO_HOME': ('equipo_placeholder.jpg', 'Foto  - Equipo - Club de robótica'),

    # == INDEX TORNEO CARD ==
    'INDEX_TORNEO_BADGE': ('METAS DEL CLUB', 'Etiqueta flotante superior de la tarjeta Torneo (Inicio).'),
    'INDEX_TORNEO_TITULO': ('Camino a la World Robot Olympiad (WRO)', 'Título principal promocional en la página de Inicio.'),
    'INDEX_TORNEO_DESC': ('Nuestros esfuerzos principales están alineados a preparar a nuestros mejores equipos para competencias internacionales como la WRO. Entrenamos resolviendo retos complejos con creatividad, lógica y tecnología de vanguardia.', 'Párrafo descriptivo de la tarjeta de Torneo.'),
    'INDEX_TORNEO_LINK_TEXT': ('Conoce más sobre la WRO', 'Texto del hipervínculo inferior de la tarjeta Torneo.'),
    'INDEX_TORNEO_LINK_URL': ('https://wro-association.org/', 'Destino web (ej. /wro o externo) asociado a la tarjeta Torneo en Inicio.'),
    'INDEX_TORNEO_TARGET': ('WRO', 'Textos grandes y llamativos (siglas) en la insignia del Inicio.'),
    'INDEX_TORNEO_TARGET_SUB': ('Target', 'Subtítulo pequeño abajo de la medalla de Inicio.'),
    
    # == CERTAMEN / TORNEO (Textos estáticos) ==
    'TORNEO_FECHA_COUNTDOWN': ('2026-08-01T00:00:00', 'Fecha meta oficial para el contador (YYYY-MM-DDTHH:MM:SS)'),
    'TORNEO_COUNTDOWN_LABEL': ('Tiempo para la fase regional', 'Etiqueta pequeña arriba del reloj.'),
    
    'TORNEO_TITULO': ('Certamen 2026', 'Texto pequeño en cápsula (badge) del Hero de Torneo.'),
    'TORNEO_SUBTITULO': ('WRO · México · 2026', 'Subtítulo tracking mono en el Hero de Torneo.'),
    'TORNEO_SLOGAN': ('Certamen de', 'Slogan gigante de la palabra base en el Hero.'),
    'TORNEO_HERO_DESC': ('Participa en la competencia de robótica más grande del mundo. Construye, programa y compite superando retos tecnológicos que transformarán tu visión del futuro.', 'Párrafo de introducción en el Top del Torneo.'),
    'TORNEO_HERO_BTN1_LABEL': ('Registrarme al club', 'Texto del botón primario en el hero del Torneo.'),
    'TORNEO_HERO_BTN2_LABEL': ('Conocer WRO →', 'Texto del botón secundario en el hero del Torneo.'),
    
    'TORNEO_INFO_TITULO': ('World Robot Olympiad 2026', 'Cabecera de la sección de información general.'),
    'TORNEO_INFO_DESC': ('La WRO es la competencia de robótica más grande del mundo. México participa en fases regionales con acceso a la final nacional.', 'Párrafo sobre la WRO.'),
    
    'TORNEO_SECTION_CAT_TITULO': ('Categorías WRO', 'Título principal de la sección de categorías.'),
    'TORNEO_SECTION_CAT_SUB': ('Competencias', 'Subtítulo para sección Competencias Internacionales (Categorías)'),
    
    'TORNEO_SECTION_FECHAS_TITULO': ('Fechas Clave', 'Título para el roadmap de fechas clave.'),
    'TORNEO_SECTION_FECHAS_SUB': ('Calendario 2026', 'Subtítulo para cronograma del torneo.'),
    
    'TORNEO_SECTION_REQ_TITULO': ('Requisitos y Beneficios', 'Título para los requisitos del torneo WRO.'),
    'TORNEO_SECTION_REQ_SUB': ('Para participar', 'Subtítulo para la sección de requisitos.'),
    
    'TORNEO_SECTION_PROY_TITULO': ('Proyectos del Club', 'Título para la galería/lista de proyectos semilla del WRO.'),
    'TORNEO_SECTION_PROY_SUB': ('Lo que construirás', 'Subtítulo para sección proyectos WRO.'),
    
    'TORNEO_CTA_TITULO': ('¿Listo para competir?', 'Cabecera final que invita a inscribirse (bottom page).'),
    'TORNEO_CTA_DESC': ('Únete al Club de Robótica, aprende a construir y programar robots, y representa al club en WRO México 2026.', 'Descripción del bloque final para conseguir miembros.'),
    'TORNEO_CTA_BTN1_LABEL': ('Registrarme ahora', 'Llamada principal a la acción al final del Torneo.'),
    'TORNEO_CTA_BTN2_LABEL': ('Ver portal del club →', 'Enlace secundario hacia Inicio al final del Torneo.')
}

def auto_seed_config(app):
    """
    Recorre el diccionario DEFAULT_CONFIGS inyectando a la Base de Datos 
    cualquier valor ausente para asegurar que Flask-Admin y el Live Editor estén 
    inmediatamente sincronizados sin necesidad de pre-ediciones manuales.
    """
    with app.app_context():
        # Consultamos todas las claves existentes
        existing_keys = set(cfg.llave for cfg in Configuracion.query.all())
        
        added_count = 0
        for raw_key, (default_val, desc) in DEFAULT_CONFIGS.items():
            if raw_key not in existing_keys:
                nueva_cfg = Configuracion(
                    llave=raw_key,
                    valor=default_val,
                    descripcion=desc
                )
                db.session.add(nueva_cfg)
                added_count += 1
                
        if added_count > 0:
            db.session.commit()
            app.logger.info(f"[*] auto_seed_config: Se han insertado {added_count} nuevas variables por defecto a la BD.")
        else:
            app.logger.info("[~] auto_seed_config: Todas las variables de interfaz están sincronizadas.")
