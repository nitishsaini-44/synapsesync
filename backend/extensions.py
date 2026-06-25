"""
extensions.py
─────────────
Centralised Flask extension instances.
Import from here instead of from app.py to prevent circular imports.
"""
from flask_socketio import SocketIO

# Initialised without the app here; bound to the app in app.py via init_app().
socketio = SocketIO()
