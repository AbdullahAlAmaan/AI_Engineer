import sqlite3, time, json
from typing import Optional

class SqliteCache:
    def __init__(self, path: str):
        self.path = path
        self._init()

    def _init(self):
        with sqlite3.connect(self.path) as con:
            con.execute("CREATE TABLE IF NOT EXISTS cache (q TEXT PRIMARY KEY, answer TEXT, citations TEXT, ts REAL)")

    def get(self, q: str):
        with sqlite3.connect(self.path) as con:
            row = con.execute("SELECT answer, citations FROM cache WHERE q=?", (q,)).fetchone()
            if row:
                return row[0], json.loads(row[1])
        return None

    def set(self, q: str, answer: str, citations: list):
        with sqlite3.connect(self.path) as con:
            con.execute("REPLACE INTO cache (q, answer, citations, ts) VALUES (?,?,?,?)", (q, answer, json.dumps(citations), time.time()))
    
    def clear_all(self):
        with sqlite3.connect(self.path) as con:
            con.execute("DELETE FROM cache")

