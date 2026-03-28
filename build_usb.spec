# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None

# --- Recolección automática de submódulos dinámicos ---
# dnspython 2.x y eventlet cargan muchos módulos dinámicamente.
# collect_submodules garantiza que TODOS los submódulos se incluyan.
dns_imports = collect_submodules('dns')
eventlet_imports = collect_submodules('eventlet')
engineeio_imports = collect_submodules('engineio')
socketio_imports = collect_submodules('socketio')

# Dependencias críticas ocultas adicionales que PyInstaller ignora por defecto
extra_hidden_imports = [
    # Eventlet hubs (cargados dinámicamente según el OS)
    'eventlet.hubs.epolls',
    'eventlet.hubs.kqueue',
    'eventlet.hubs.selects',
    'eventlet.hubs.poll',
    'eventlet.hubs.hub',
    'eventlet.hubs.asyncio',
    # Submódulos de dns específicos para dnspython 2.x
    'dns.rdtypes',
    'dns.rdtypes.ANY',
    'dns.rdtypes.IN',
    'dns.rdtypes.ANY.SOA',
    'dns.rdtypes.ANY.MX',
    'dns.rdtypes.ANY.NS',
    'dns.rdtypes.ANY.CNAME',
    'dns.rdtypes.ANY.TXT',
    'dns.rdtypes.IN.A',
    'dns.rdtypes.IN.AAAA',
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
    'dns.resolver',
    'dns.query',
    'dns.message',
    'dns.name',
    'dns.rdata',
    'dns.rdataclass',
    'dns.rdataset',
    'dns.rdatatype',
    'dns.tokenizer',
    'dns.exception',
    'dns.flags',
    'dns.inet',
    'dns.ipv4',
    'dns.ipv6',
    'dns.opcode',
    'dns.entropy',
    'dns.set',
    'dns.ttl',
    # Flask y SQLAlchemy
    'flask_socketio',
    'sqlalchemy.sql.default_comparator',
    'sqlalchemy.dialects.sqlite',
    'sqlalchemy.dialects.sqlite.pysqlite',
    'sqlalchemy.orm',
    'flask_sqlalchemy',
    'pymysql',
    # Encodings requeridos por Windows
    'encodings',
    'encodings.utf_8',
    'encodings.ascii',
    'encodings.latin_1',
]

hidden_imports = dns_imports + eventlet_imports + engineeio_imports + socketio_imports + extra_hidden_imports

# Datos adjuntos: Las carpetas de plantillas y archivos estáticos de Flask
flask_admin_data = collect_data_files('flask_admin')
flask_wtf_data = collect_data_files('flask_wtf')
wtforms_data = collect_data_files('wtforms')

added_files = [
    ('app/templates', 'app/templates'),
    ('app/static', 'app/static'),
    ('migrations', 'migrations')
] + flask_admin_data + flask_wtf_data + wtforms_data


a = Analysis(
    ['run_offline.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=hidden_imports,
    hookspath=['hooks'],
    hooksconfig={},
    runtime_hooks=['runtime_hooks/rthook_dns_fix.py'],
    excludes=[
        # Excluir módulos que no usamos para reducir tamaño
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'test',
        'unittest',
    ],
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
    debug=True,
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
