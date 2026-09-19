import aiosqlite
from memory_engine.sqlite_manager import SQLiteManager

class AdaptiveLearner:
    """
    Premium Feature: Self-Learning AI Behavior Engine.
    Analyzes the user's chat history to extract their communication style, 
    pacing, and emotional triggers, then creates an evolving behavior profile.
    """
    def __init__(self, phone_number: str, db_path: str):
        self.phone_number = phone_number
        self.db_path = db_path
        # The AI will re-analyze and evolve its personality after every 10 new user messages
        self.trigger_threshold = 10  

    async def _ensure_profile_table(self):
        """
        Dynamically adds an 'adaptive_profile' table inside the user's isolated 
        SQLite database without breaking existing message architecture.
        """
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS adaptive_profile (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    behavior_summary TEXT NOT NULL,
                    messages_analyzed INTEGER NOT NULL DEFAULT 0
                )
            ''')
            await db.commit()

    async def get_learned_profile(self) -> str:
        """
        Retrieves the learned psychological profile to inject into the main AI System Prompt.
        """
        await self._ensure_profile_table()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT behavior_summary FROM adaptive_profile WHERE id = 1")
            row = await cursor.fetchone()
            
            # If no profile exists yet, return a neutral fallback
            return row["behavior_summary"] if row else "Maintain a natural, engaging tone."

    async def evolve_personality(self, ai_generate_function):
        """
        The core intelligence engine. Reads recent history, runs a psychological 
        meta-analysis via the AI API, and permanently updates the user's profile.
        """
        await self._ensure_profile_table()
        
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            # 1. Check how many total user messages exist
            cursor = await db.execute("SELECT COUNT(*) as total FROM messages WHERE role = 'user'")
            row = await cursor.fetchone()
            total_user_msgs = row["total"] if row else 0
            
            # 2. Get the last analyzed count and current summary
            cursor = await db.execute("SELECT messages_analyzed, behavior_summary FROM adaptive_profile WHERE id = 1")
            profile_row = await cursor.fetchone()
            
            last_analyzed = profile_row["messages_analyzed"] if profile_row else 0
            current_summary = profile_row["behavior_summary"] if profile_row else "No previous data."

            # 3. Only run heavy analysis if the threshold is met (saves API costs)
            if (total_user_msgs - last_analyzed) >= self.trigger_threshold:
                
                # Fetch the latest 20 interactions for context
                cursor = await db.execute('''
                    SELECT role, content FROM (
                        SELECT * FROM messages ORDER BY id DESC LIMIT 20
                    ) ORDER BY id ASC
                ''')
                history_rows = await cursor.fetchall()
                chat_history_text = "\n".join([f"{r['role']}: {r['content']}" for r in history_rows])
                
                # 4. The Meta-Prompt: Asking the AI to act as a psychological analyst
                analysis_prompt = (
                    "You are a behavioral analyst. Analyze this chat history for a romance storyline. "
                    "Determine the user's communication style, emotional state, and what kind of "
                    "romantic responses they respond best to (e.g., poetic, dominant, shy, casual, highly emotional). "
                    "Write a 2-sentence instruction for an AI bot on how to adapt its personality for this specific user. "
                    "Previous Personality Instruction: " + current_summary
                )
                
                try:
                    # 5. Generate the new, evolved profile
                    new_behavior_summary = await ai_generate_function(
                        system_prompt=analysis_prompt, 
                        user_text=chat_history_text
                    )
                    
                    # 6. Save the evolved profile back to the isolated database
                    if profile_row:
                        await db.execute(
                            "UPDATE adaptive_profile SET behavior_summary = ?, messages_analyzed = ? WHERE id = 1",
                            (new_behavior_summary, total_user_msgs)
                        )
                    else:
                        await db.execute(
                            "INSERT INTO adaptive_profile (id, behavior_summary, messages_analyzed) VALUES (1, ?, ?)",
                            (new_behavior_summary, total_user_msgs)
                        )
                    await db.commit()
                    print(f"🧠 [Intelligence] Evolved Personality for {self.phone_number}: {new_behavior_summary}")
                
                except Exception as e:
                    print(f"⚠️ [Intelligence] Failed to evolve personality for {self.phone_number}: {e}")