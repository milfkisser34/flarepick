
import sqlite3
from pathlib import Path


class Database:
    def __init__(self, path: str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)

        self.conn = sqlite3.connect(path, timeout=1)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")

        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS collections (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE
                    CHECK (length(name) BETWEEN 1 AND 80)
            );

            CREATE TABLE IF NOT EXISTS photos (
                id INTEGER PRIMARY KEY,
                collection_id INTEGER NOT NULL,
                path TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'unmarked'
                    CHECK (status IN ('unmarked', 'picked', 'rejected')),
                UNIQUE (collection_id, path),
                FOREIGN KEY (collection_id)
                    REFERENCES collections(id) ON DELETE CASCADE
            );
        """)

    def get_collections(self):
        return self.conn.execute(
            "SELECT * FROM collections ORDER BY id"
        ).fetchall()

    def create_collection(self, name: str):
        name = name.strip()

        if not name or "\n" in name or "\r" in name:
            raise ValueError("Invalid collection name")

        with self.conn:
            return self.conn.execute(
                "INSERT INTO collections (name) VALUES (?)",
                (name,)
            ).lastrowid

    def rename_collection(self, collection_id: int, name: str):
        name = name.strip()

        if not name or "\n" in name or "\r" in name:
            raise ValueError("Invalid collection name")

        with self.conn:
            self.conn.execute(
                "UPDATE collections SET name = ? WHERE id = ?",
                (name, collection_id)
            )

    def delete_collection(self, collection_id: int):
        with self.conn:
            self.conn.execute(
                "DELETE FROM collections WHERE id = ?",
                (collection_id,)
            )

    def get_photos(self, collection_id: int, status: str = "all"):
        if status != "all":
            return self.conn.execute(
                "SELECT * FROM photos WHERE collection_id = ? AND status = ? ORDER BY id",
                (collection_id, status)
            ).fetchall()

        return self.conn.execute(
            "SELECT * FROM photos WHERE collection_id = ? ORDER BY id",
            (collection_id,)
        ).fetchall()

    def add_photo(self, collection_id: int, path: str):
        path = str(Path(path).resolve())

        with self.conn:
            return self.conn.execute(
                "INSERT INTO photos (collection_id, path) VALUES (?, ?) "
                "ON CONFLICT(collection_id, path) DO NOTHING",
                (collection_id, path)
            ).rowcount > 0

    def set_status(self, photo_id: int, collection_id: int, status: str):
        with self.conn:
            self.conn.execute(
                "UPDATE photos SET status = ? WHERE id = ? AND collection_id = ?",
                (status, photo_id, collection_id)
            )

    def remove_photo(self, photo_id: int, collection_id: int):
        with self.conn:
            self.conn.execute(
                "DELETE FROM photos WHERE id = ? AND collection_id = ?",
                (photo_id, collection_id)
            )

    def close(self):
        self.conn.close()
