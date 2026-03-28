# runtime_hooks/rthook_dns_fix.py
# Este hook se ejecuta ANTES que cualquier otro código al iniciar el .exe
# Su propósito es parchar el problema de dnspython 2.x + eventlet en PyInstaller

import sys
import types

# dnspython 2.x eliminó dns.btree pero eventlet lo busca dinámicamente.
# Creamos un módulo falso para que eventlet no falle al importar.
# greendns.py de eventlet hace: from dns.btree import ... (en versiones antiguas)
# En dnspython 2.x esto ya no existe; greendns usa el resolver nativo si no lo encuentra.
if 'dns.btree' not in sys.modules:
    try:
        import dns
        # Intentar importar normalmente primero
        import dns.resolver
    except ImportError:
        pass
    
    # Crear un módulo stub para dns.btree si no existe
    # Esto evita el ModuleNotFoundError en eventlet/support/greendns.py
    stub = types.ModuleType('dns.btree')
    stub.BTreeCoveredRdataset = None
    sys.modules['dns.btree'] = stub
