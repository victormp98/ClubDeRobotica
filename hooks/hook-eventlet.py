# hooks/hook-eventlet.py
# Hook personalizado para eventlet + dnspython 2.x
# Garantiza que todos los submodulos sean detectados por PyInstaller

from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Recolectar TODOS los submódulos de eventlet
hiddenimports = collect_submodules('eventlet')

# Recolectar TODOS los submódulos de dns (dnspython 2.x)
hiddenimports += collect_submodules('dns')
