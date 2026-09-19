import os
import aiofiles

# Base Directory Paths
BASE_DIR = os.path.dirname(__file__)
GLOBAL_FILE = os.path.join(BASE_DIR, "default_global.txt")
OVERRIDES_DIR = os.path.join(BASE_DIR, "overrides")

# Ensure the overrides directory exists automatically
os.makedirs(OVERRIDES_DIR, exist_ok=True)

class StorylineResolver:
    """
    Engine for intelligently merging global storylines with user-specific 
    overrides and adaptive psychological profiles. Async-safe.
    """
    
    @staticmethod
    async def _read_file_async(filepath: str) -> str:
        """Helper to read text files asynchronously to prevent event-loop blocking."""
        if not os.path.exists(filepath):
            return ""
        # Using aiofiles ensures that reading a heavy text file doesn't pause the bot
        async with aiofiles.open(filepath, mode='r', encoding='utf-8') as f:
            return await f.read()

    @classmethod
    async def get_system_prompt(cls, phone_number: str, learned_profile: str = "") -> str:
        """
        Builds the ultimate system prompt by combining:
        1. Global Default Storyline
        2. User-Specific Override (if exists)
        3. Dynamically Learned Behavior Profile
        """
        # Step 1: Read Global Core Rules
        global_rules = await cls._read_file_async(GLOBAL_FILE)
        if not global_rules:
            # Fallback if the client accidentally deletes the global file
            global_rules = "You are a friendly, natural, and romantic conversational partner. Speak like a real human."

        # Step 2: Check for VIP/Specific Overrides
        safe_number = "".join(c for c in phone_number if c.isdigit() or c == '+')
        override_path = os.path.join(OVERRIDES_DIR, f"{safe_number}.txt")
        user_override = await cls._read_file_async(override_path)

        # Step 3: Smart Merging Architecture
        final_prompt_parts = [
            "[CORE INSTRUCTIONS]",
            global_rules.strip()
        ]

        # If client made a custom file for this number, inject it with high priority
        if user_override:
            final_prompt_parts.extend([
                "\n[SPECIFIC USER OVERRIDE - HIGH PRIORITY]",
                "Apply these specific instructions exclusively for this user:",
                user_override.strip()
            ])

        # Inject the self-learned psychological profile from the Intelligence module
        if learned_profile:
            final_prompt_parts.extend([
                "\n[ADAPTIVE BEHAVIOR PROFILE]",
                "Based on past interactions with this specific user, adjust your personality as follows:",
                learned_profile.strip()
            ])

        # Compile everything into one powerful prompt for OpenRouter/DeepSeek
        return "\n".join(final_prompt_parts)