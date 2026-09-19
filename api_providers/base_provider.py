from abc import ABC, abstractmethod

class BaseProvider(ABC):
    """
    Master template for all AI Providers. 
    Enforces a strict structure so the bot never crashes when switching APIs.
    """
    
    @abstractmethod
    async def generate_response(self, system_prompt: str, chat_history: list, user_text: str) -> str:
        """
        Every API adapter MUST implement this method.
        :param system_prompt: The merged rules (Global + User Override + Adaptive Profile)
        :param chat_history: List of dictionaries [{"role": "user", "content": "..."}, ...]
        :param user_text: The latest message from the user
        :return: AI generated text response
        """
        pass