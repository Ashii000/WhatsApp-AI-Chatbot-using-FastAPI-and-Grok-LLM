import os
import aiosqlite
from datetime import datetime

# Dynamically create the 'databases' folder inside 'memory_engine' if it doesn't exist
DB_DIR = os.path.join(os.path.dirname(__file__), "databases")
os.makedirs(DB_DIR, exist_ok=True)

class SQLiteManager:
    """
    Handles perfectly isolated memory for each individual user.
    Implements aiosqlite for async non-blocking operations and WAL mode to prevent locks.
    """
    def __init__(self, phone_number: str):
        # Sanitize the phone number to create a safe database file name
        safe_number = "".join(c for c in phone_number if c.isdigit() or c == '+')
        self.db_path = os.path.join(DB_DIR, f"{safe_number}.db")

    async def _initialize_db(self):
        """
        Creates the database and table for a new user if it doesn't exist.
        Crucially enables WAL mode for high-performance concurrency.
        """
        async with aiosqlite.connect(self.db_path) as db:
            # Enable Write-Ahead Logging (WAL) to prevent "database locked" crashes
            await db.execute("PRAGMA journal_mode=WAL;")
            # Optimize sync settings for faster writes without losing data integrity
            await db.execute("PRAGMA synchronous=NORMAL;")
            
            # Create the exact schema needed for AI chat history
            await db.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            await db.commit()

    async def save_interaction(self, role: str, content: str):
        """
        Saves a single message ('user' or 'assistant') securely into the isolated file.
        """
        await self._initialize_db()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO messages (role, content) VALUES (?, ?)",
                (role, content)
            )
            await db.commit()

    async def get_recent_context(self, limit: int = 15) -> list:
        """
        Extracts the most recent chat history to feed into the AI's context window.
        Automatically formats the output to match OpenRouter/ChatGPT exact API requirements.
        """
        await self._initialize_db()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            # SQL Logic: Get the last 'limit' messages, but return them in ascending order
            cursor = await db.execute('''
                SELECT role, content FROM (
                    SELECT * FROM messages ORDER BY id DESC LIMIT ?
                ) ORDER BY id ASC
            ''', (limit,))
            
            rows = await cursor.fetchall()
            
            # Format output as: [{"role": "user", "content": "hello"}, ...]
            return [{"role": row["role"], "content": row["content"]} for row in rows]

    async def clear_memory(self):
        """
        Optional utility to wipe a specific user's memory if they want to restart the storyline.
        """
        if os.path.exists(self.db_path):
            os.remove(self.db_path)