import os
import httpx
import json
from api_providers.base_provider import BaseProvider

class OpenRouterAdapter(BaseProvider):
    """
    Handles secure and async communication with OpenRouter's API.
    Specifically tuned for uncensored and high-speed romance models.
    """
    
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        
        # Load specific AI settings from our JSON config
        config_path = os.path.join(os.path.dirname(__file__), "..", "config", "settings.json")
        with open(config_path, "r") as f:
            self.settings = json.load(f)["ai_configuration"]

    async def generate_response(self, system_prompt: str, chat_history: list, user_text: str) -> str:
        if not self.api_key:
            return "System Error: OpenRouter API Key is missing in .env file."

        # Compile the exact message array required by OpenRouter
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(chat_history)
        messages.append({"role": "user", "content": user_text})

        payload = {
            "model": self.settings.get("model", "gryphe/mythomax-l2-13b"),
            "messages": messages,
            "temperature": self.settings.get("temperature", 0.85),
            "max_tokens": self.settings.get("max_generation_tokens", 150)
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/whatsapp-bot", # Required by OpenRouter
            "X-Title": "WhatsApp AI Engine",
            "Content-Type": "application/json"
        }

        # Non-blocking async API Call with a timeout safety net
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.api_url, headers=headers, json=payload, timeout=20.0)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"].strip()
            except Exception as e:
                print(f"❌ OpenRouter API Error: {e}")
                return "I'm having a little trouble thinking right now, give me a second..."