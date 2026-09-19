import os
import asyncio
import random
import httpx
from core.rate_limiter import meta_limiter
from dotenv import load_dotenv

load_dotenv(dotenv_path="config/.env")

# Configurations
WAHA_BASE_URL = "http://localhost:3000"
WAHA_API_URL = f"{WAHA_BASE_URL}/api/sendText"
# Ensure the new API Key is loaded
API_KEY = os.getenv("WAHA_API_KEY", "1290aa811bc94f7fa4a7edc15d16b62d")
SESSION_NAME = "default"

async def simulate_typing(chat_id: str, message_length: int):
    """
    AI Typing Simulator: Shows 'Typing...' status before sending the message.
    """
    headers = {"X-Api-Key": API_KEY, "Content-Type": "application/json"}
    payload = {"session": SESSION_NAME, "chatId": chat_id}
    
    async with httpx.AsyncClient() as client:
        try:
            # Start Typing
            await client.post(f"{WAHA_BASE_URL}/api/startTyping", json=payload, headers=headers)
            
            # Dynamic human typing speed (0.05 to 0.15 seconds per character)
            typing_time = message_length * random.uniform(0.05, 0.15)
            # Max 8 seconds of typing so it doesn't look stuck
            await asyncio.sleep(min(typing_time, 8.0)) 
            
            # Stop Typing
            await client.post(f"{WAHA_BASE_URL}/api/stopTyping", json=payload, headers=headers)
        except Exception as e:
            print(f"⚠️ WAHA Typing API Error: {e}")

async def send_whatsapp_message(to_number: str, message_text: str):
    """
    Sends a text message back to the user via WAHA Local Server.
    Guarded by the rate limiter and Human-Like Anti-Ban delays.
    """
    # Wait if we are sending too many messages concurrently
    await meta_limiter.wait()
    
    # Clean number and add WAHA format suffix
    clean_number = to_number.replace("+", "").replace(" ", "")
    chat_id = f"{clean_number}@c.us"
    
    headers = {
        "X-Api-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    # --- ANTI-BAN LOGIC START ---
    
    # Step A: Human Reading Delay (3 to 7 seconds before typing starts)
    read_delay = random.uniform(3.0, 7.0)
    print(f"⏳ Waiting {round(read_delay, 1)}s to read message from {clean_number}...")
    await asyncio.sleep(read_delay)
    
    # Step B: Show Typing Indicator
    print(f"⌨️ Simulating typing for {clean_number}...")
    await simulate_typing(chat_id, len(message_text))
    
    # --- ANTI-BAN LOGIC END ---

    # WAHA Payload format
    payload = {
        "chatId": chat_id,
        "text": message_text,
        "session": SESSION_NAME
    }
    
    # Use Async HTTP Client for non-blocking high speed requests
    async with httpx.AsyncClient() as client:
        try:
            # We connect to localhost WAHA container
            response = await client.post(WAHA_API_URL, headers=headers, json=payload, timeout=30.0)
            response.raise_for_status()
            result = response.json()
            print(f"✅ WAHA message securely sent to {clean_number}")
            return result
        except httpx.HTTPStatusError as e:
            print(f"❌ WAHA API Error for {clean_number}: {e.response.text}")
            print(f"   Status Code: {e.response.status_code}")
            return None
        except Exception as e:
            print(f"❌ WAHA API Connection Error for {clean_number}: {str(e)}")
            return None