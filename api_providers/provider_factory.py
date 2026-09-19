import json
import os
from api_providers.openrouter_adapter import OpenRouterAdapter
from api_providers.deepseek_adapter import DeepSeekAdapter
from api_providers.grok_adapter import GrokAdapter  # <-- Import the new adapter

class ProviderFactory:
    """
    Dynamically instantiates the correct AI Provider based on settings.json.
    Enables zero-code-change switching between AI models.
    """
    
    @staticmethod
    def get_active_provider():
        config_path = os.path.join(os.path.dirname(__file__), "..", "config", "settings.json")
        
        try:
            with open(config_path, "r") as f:
                settings = json.load(f)
                active_provider_name = settings["ai_configuration"]["active_provider"].lower()
        except Exception as e:
            print(f"⚠️ Error reading config, defaulting to OpenRouter: {e}")
            active_provider_name = "openrouter"

        # The Switch Engine
        if active_provider_name == "openrouter":
            print("🔌 Initializing OpenRouter Connection...")
            return OpenRouterAdapter()
        elif active_provider_name == "deepseek":
            print("🔌 Initializing DeepSeek Connection...")
            return DeepSeekAdapter()
        elif active_provider_name == "grok":       # <-- Add Grok to the engine
            print("🔌 Initializing xAI Grok Connection...")
            return GrokAdapter()
        else:
            print(f"⚠️ Unknown provider '{active_provider_name}', falling back to OpenRouter.")
            return OpenRouterAdapter()

# Global singleton instance ready to be imported by the Worker Pool
ai_factory = ProviderFactory.get_active_provider()