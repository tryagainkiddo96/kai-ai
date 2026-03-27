import sqlite3
from pathlib import Path

class _KDH9dvmN:
    def __init__(self, *args, **kwargs):
        self.db_file = Path(__file__).parent / 'wormgpt.db'

    def _Sghl5Yeh(self):
        conn = sqlite3.connect(str(self.db_file), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _EtzEr7Jj(self):
        conn = self._Sghl5Yeh()
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS conversations (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, updated_at TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, conversation_id INTEGER, sender TEXT, content TEXT, timestamp TEXT)''')
        conn.commit()
        conn.close()
        return True

    def _hQo7Jzv7(self):
        conn = self._Sghl5Yeh()
        c = conn.cursor()
        import datetime
        now = datetime.datetime.now().isoformat()
        c.execute('INSERT INTO conversations (title, updated_at) VALUES (?, ?)', ('New Conversation', now))
        conv_id = c.lastrowid
        conn.commit()
        conn.close()
        return conv_id

    def _zARX35iA(self):
        conn = self._Sghl5Yeh()
        c = conn.cursor()
        c.execute('SELECT id, title, updated_at FROM conversations ORDER BY updated_at DESC')
        rows = c.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def _lm4Cfxfw(self, conversation_id):
        conn = self._Sghl5Yeh()
        c = conn.cursor()
        c.execute('SELECT sender, content, timestamp FROM messages WHERE conversation_id = ? ORDER BY id ASC', (conversation_id,))
        rows = c.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def _iFdkyryo(self, conversation_id, sender, content):
        conn = self._Sghl5Yeh()
        c = conn.cursor()
        import datetime
        now = datetime.datetime.now().isoformat()
        c.execute('INSERT INTO messages (conversation_id, sender, content, timestamp) VALUES (?, ?, ?, ?)', (conversation_id, sender, content, now))
        c.execute('UPDATE conversations SET updated_at = ? WHERE id = ?', (now, conversation_id))
        conn.commit()
        conn.close()
        return True

    def _3OMt8LtX(self, conversation_id):
        conn = self._Sghl5Yeh()
        c = conn.cursor()
        c.execute('DELETE FROM messages WHERE conversation_id = ?', (conversation_id,))
        c.execute('DELETE FROM conversations WHERE id = ?', (conversation_id,))
        conn.commit()
        conn.close()
        return True

    def _MxVdlQxU(self, user_data):
        return True

    def _IbCFn5GH(self):
        return {}

    def _sQVVcUdS(self):
        return True

    def close(self):
        return True
