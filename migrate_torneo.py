from run import app
from app.extensions import db
from app.models.torneo import CategoriaTorneo, FechaTorneo, RecuadroTorneo, RequisitoTorneo, ProyectoTorneo
from app.models.configuracion import Configuracion

with app.app_context():
    db.create_all()
    
    # Auto-seed models if empty
    if CategoriaTorneo.query.count() == 0:
        db.session.add(CategoriaTorneo(nombre='RoboMission', edades='8 a 19 años', mision='Construye y programa un robot autónomo que resuelva retos en un campo predefinido combinando mecánica y estrategia.', imagen_path='img/bg-tech.jpg', orden=1))
        db.session.add(CategoriaTorneo(nombre='Future Innovators', edades='8 a 19 años', mision='Desarrolla un proyecto de investigación y construye un prototipo robótico funcional enfocado a resolver un problema real.', imagen_path='img/code.jpg', orden=2))
        db.session.add(CategoriaTorneo(nombre='RoboSports', edades='11 a 19 años', mision='Competencia directa de robots en juegos deportivos dinámicos. Tu robot deberá enfrentarse a otro equipo.', imagen_path='img/circuit.jpg', orden=3))
        db.session.add(CategoriaTorneo(nombre='Future Engineers', edades='14 a 19 años', mision='Reto avanzado de ingeniería empleando vehículos autónomos miniatura que navegan utilizando IA y visión por computadora.', imagen_path='img/team.jpg', orden=4))
        
    if FechaTorneo.query.count() == 0:
        db.session.add(FechaTorneo(fecha='Abr – May 2026', nombre='Inscripciones al Club', descripcion='Registro web y formación de equipos', estado_clase='f-open', estado_etiqueta='✓ Abierto', orden=1))
        db.session.add(FechaTorneo(fecha='Mayo 2026', nombre='Inscripciones Torneo', descripcion='Portal oficial - equipos de 2–3 integrantes', estado_clase='f-open', estado_etiqueta='✓ Abierto', orden=2))
        db.session.add(FechaTorneo(fecha='May – Jun 2026', nombre='Capacitación de equipos', descripcion='Talleres en laboratorio (programación y mecánica)', estado_clase='f-coming', estado_etiqueta='En preparación', orden=3))
        db.session.add(FechaTorneo(fecha='Jul – Ago 2026', nombre='Fase Regional', descripcion='Competencia clasificatoria a nivel regional', estado_clase='f-coming', estado_etiqueta='Próximamente', orden=4))
        db.session.add(FechaTorneo(fecha='Septiembre 2026', nombre='Final Nacional', descripcion='Equipos compiten por la representación nacional', estado_clase='f-future', estado_etiqueta='Futuro', orden=5))

    if RecuadroTorneo.query.count() == 0:
        db.session.add(RecuadroTorneo(icono='fa-solid fa-users', etiqueta='MIEMBROS', valor='+120', orden=1))
        db.session.add(RecuadroTorneo(icono='fa-solid fa-trophy', etiqueta='PREMIOS', valor='35', orden=2))
        db.session.add(RecuadroTorneo(icono='fa-solid fa-robot', etiqueta='ROBOTS', valor='50', orden=3))
        db.session.add(RecuadroTorneo(icono='fa-solid fa-globe', etiqueta='SEDES', valor='5', orden=4))

    if RequisitoTorneo.query.count() == 0:
        db.session.add(RequisitoTorneo(texto='Estar inscrito formalmente en cualquier ingeniería del Instituto o nivel pertinente.', orden=1))
        db.session.add(RequisitoTorneo(texto='Contar con disponibilidad de horario extra-escolar.', orden=2))
        db.session.add(RequisitoTorneo(texto='Conocimientos elementales adquiridos o interés verificable en robótica.', orden=3))

    db.session.commit()
    print("Migración de Torneo exitosa!")
