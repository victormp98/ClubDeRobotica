# -*- mode: python ; coding: utf-8 -*-

import os

block_cipher = None

# Dependencias críticas ocultas de Eventlet y SocketIO que PyInstaller ignora por defecto
hidden_imports = [
    'engineio.async_drivers.eventlet',
    'eventlet.hubs.epolls',
    'eventlet.hubs.kqueue',
    'eventlet.hubs.selects',
    'dns',
    'dns.dnssec',
    'dns.e164',
    'dns.hash',
    'dns.namedict',
    'dns.tsigkeyring',
    'dns.update',
    'dns.version',
    'dns.zone',
    'dns.asyncbackend',
    'dns.asyncquery',
    'dns.asyncresolver',
    'flask_socketio',
    'sqlalchemy.sql.default_comparator',
    'sqlalchemy.dialects.sqlite',
    'flask_sqlalchemy',
    'pymysql'
]

# Datos adjuntos: Las carpetas de plantillas y archivos estáticos de Flask
added_files = [
    ('app/templates', 'app/templates'),
    ('app/static', 'app/static'),
    ('migrations', 'migrations')
]

a = Analysis(
    ['run_offline.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# IMPORTANTE: Estamos generando una 'CARPETA' (onedir) en lugar de un único exe, 
# tal cual lo recordabas en tu experiencia anterior. Esto da más estabilidad y rapidez.
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ClubRobotica_Comando',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True, # Mantiene la consola negra para detener o ver los mensajes
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None # Puedes meter tu propio (.ico) aquí después
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ClubRobotica_Portable_USB',
)
