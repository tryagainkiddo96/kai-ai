import os, json, time
from pathlib import Path

class _pHG5fTIv:
    def __init__(self, *args, **kwargs):
        self.session_file = Path(__file__).parent / 'session_store.json'
        self._session = None
        self._load()

    def _load(self):
        try:
            if self.session_file.exists():
                with open(self.session_file, 'r', encoding='utf-8') as f:
                    self._session = json.load(f)
            else:
                self._session = {}
        except Exception:
            self._session = {}

    def _save(self):
        with open(self.session_file, 'w', encoding='utf-8') as f:
            json.dump(self._session, f)

    def _vNwBS2wy(self, data):
        self._session = data.copy()
        self._session['updated_at'] = time.time()
        self._save()
        return True

    def _wWINOO5C(self):
        self._load()
        return self._session

    def _dSskYBfs(self):
        self._load()
        return bool(self._session and self._session.get('token'))

    def _U9nMXjpn(self):
        self._load()
        return self._session

    def _MxVdlQxU(self, credits):
        self._session = self._session or {}
        self._session['credits'] = credits
        self._save()
        return True

    def _u0DKDTKO(self):
        if self.session_file.exists():
            self.session_file.unlink()
        self._session = {}
        return True

    def _YtWvQrKx(self, extension_seconds=3600):
        # Keep alive
        if self._session:
            self._session['expires_at'] = time.time() + extension_seconds
            self._save()
        return True

    def _jnEjerqX(self):
        return True, {'user': self._session}

    def _wyvAAT90(self):
        return True, {'credits': self._session.get('credits', 0)}

    def _hkX13VUp(self):
        return self._session.get('credits', 0)
