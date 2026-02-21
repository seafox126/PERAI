from __future__ import annotations

import sqlite3
from pathlib import Path


class FileModule:
    def __init__(self, db_path: Path, root: Path) -> None:
        self.db_path = db_path
        self.root = root
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def execute(self, parameters: dict) -> str:
        action = parameters.get("action")
        if action == "index":
            return self._index()
        if action == "find":
            query = str(parameters.get("query", "")).strip()
            if not query:
                return "Which file?"
            return self._find(query)
        if action == "open":
            path = str(parameters.get("path", "")).strip()
            return self._open(path)
        return "Unknown file action."

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS files(path TEXT PRIMARY KEY, name TEXT)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_files_name ON files(name)")

    def _index(self) -> str:
        count = 0
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM files")
            for p in self.root.rglob("*"):
                if p.is_file():
                    conn.execute("INSERT OR REPLACE INTO files(path, name) VALUES(?, ?)", (str(p), p.name.lower()))
                    count += 1
            conn.commit()
        return f"Indexed {count} files."

    def _find(self, query: str) -> str:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT path FROM files WHERE name LIKE ? ORDER BY LENGTH(name) LIMIT 1",
                (f"%{query.lower()}%",),
            ).fetchone()
        return row[0] if row else "Not found."

    def _open(self, path: str) -> str:
        if not path:
            return "Which file?"
        target = Path(path)
        if not target.exists() or not target.is_file():
            return "Not found."
        return f"Opening {target.name}."
