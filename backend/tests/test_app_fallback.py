import os
import importlib


def test_init_app_uses_fallback(monkeypatch):
    # Ensure MONGODB_URI not set so fallback storage is used
    monkeypatch.delenv('MONGODB_URI', raising=False)
    # Reload app module to run init_app fresh
    app = importlib.import_module('app')
    # Force the Config class used by app to behave as if no MONGODB_URI is set.
    if hasattr(app, 'Config'):
        app.Config.MONGODB_URI = None
    else:
        # Also try to set backend.config.Config if imported differently
        try:
            import config
            config.Config.MONGODB_URI = None
        except Exception:
            pass
    # Ensure fallback lists are empty
    app._fallback_chats = []
    app.init_app()
    assert app.chats_collection is None
    # Add a chat using the helper and confirm it's stored in fallback with env tag
    chat = app.add_chat('group123', 1, 2)
    assert chat in app._fallback_chats
    assert chat.get('env') == app.app.config.get('APP_ENV')
