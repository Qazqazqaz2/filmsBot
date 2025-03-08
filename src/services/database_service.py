import sqlite3
import aiosqlite
from typing import List
from ..interfaces import IMovieDatabase

class SQLiteMovieDatabase(IMovieDatabase):
    def __init__(self, db_path: str = "movies.db"):
        self.db_path = db_path
        self.levels = ["A1", "A2", "B1", "B2", "C1", "C2"]

    async def init_db(self) -> None:
        """Initialize database and create tables if not exist"""
        async with aiosqlite.connect(self.db_path) as db:
            for level in self.levels:
                await db.execute(f"""
                    CREATE TABLE IF NOT EXISTS level_{level} (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        movie_name TEXT NOT NULL UNIQUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
            await db.commit()

    async def save_movie(self, level: str, movie_name: str) -> None:
        """Save movie to specific level table"""
        if level not in self.levels:
            raise ValueError(f"Invalid level: {level}")

        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute(
                    f"INSERT INTO level_{level} (movie_name) VALUES (?)",
                    (movie_name,)
                )
                await db.commit()
            except sqlite3.IntegrityError:
                # Фильм уже существует в базе
                pass

    async def get_movies(self, level: str) -> List[str]:
        """Get all movies for specific level"""
        if level not in self.levels:
            raise ValueError(f"Invalid level: {level}")

        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                f"SELECT movie_name FROM level_{level} ORDER BY created_at DESC"
            ) as cursor:
                rows = await cursor.fetchall()
                return [row[0] for row in rows] 