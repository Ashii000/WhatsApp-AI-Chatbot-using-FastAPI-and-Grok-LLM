import os
import httpx
import json
from api_providers.base_provider import BaseProvider

class GrokAdapter(BaseProvider):
    """
    Adapter for xAI's Grok API.
    Provides high-speed, witty, and uncensored responses based on settings.
    """
    
    def __init__(self):
        self.api_key = os.getenv("GROK_API_KEY")
        self.api_url = "https://api.x.ai/v1/chat/completions"
        
        config_path = os.path.join(os.path.dirname(__file__), "..", "config", "settings.json")
        with open(config_path, "r") as f:
            self.settings = json.load(f)["ai_configuration"]

    async def generate_response(self, system_prompt: str, chat_history: list, user_text: str) -> str:
        if not self.api_key:
            return "System Error: Grok API Key is missing in .env file."

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(chat_history)
        messages.append({"role": "user", "content": user_text})

        payload = {
            "model": "grok-beta", # You can also use grok-2-latest if available
            "messages": messages,
            "temperature": self.settings.get("temperature", 0.85),
            "max_tokens": self.settings.get("max_generation_tokens", 150)
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.api_url, headers=headers, json=payload, timeout=20.0)
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"].strip()
            except Exception as e:
                print(f"❌ Grok API Error: {e}")
                return "My circuits are a bit crossed right now, give me a moment..."