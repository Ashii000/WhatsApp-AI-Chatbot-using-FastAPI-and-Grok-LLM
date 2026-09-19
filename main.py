import asyncio
import random
import httpx # (Asynchronous requests ke liye)

WAHA_URL = "http://localhost:3000"
API_KEY = "1290aa811bc94f7fa4a7edc15d16b62d" # Yahan .env se key load karein
SESSION_NAME = "default"

async def simulate_typing(chat_id: str, message_length: int):
    """Asynchronous Typing Simulator - Server ko block nahi karega"""
    headers = {"X-Api-Key": API_KEY, "Content-Type": "application/json"}
    payload = {"session": SESSION_NAME, "chatId": chat_id}
    
    async with httpx.AsyncClient() as client:
        # Start Typing
        await client.post(f"{WAHA_URL}/api/startTyping", json=payload, headers=headers)
        
        # Human typing speed delay (Non-blocking)
        typing_time = message_length * random.uniform(0.1, 0.3)
        await asyncio.sleep(min(typing_time, 8.0)) # Max 8 seconds ki typing
        
        # Stop Typing
        await client.post(f"{WAHA_URL}/api/stopTyping", json=payload, headers=headers)

async def send_secure_reply(phone_number: str, text_message: str):
    """Perfect Anti-Ban Reply Pipeline"""
    chat_id = f"{phone_number}@c.us"
    headers = {"X-Api-Key": API_KEY, "Content-Type": "application/json"}
    
    # 1. AI Human Delay: Message parhne aur sochne ka time (5 se 15 seconds)
    read_delay = random.uniform(5.0, 15.0)
    print(f"⏳ Waiting {round(read_delay, 1)}s to read message like a human...")
    await asyncio.sleep(read_delay)
    
    # 2. Typing start karein
    print("⌨️ Simulating typing...")
    await simulate_typing(chat_id, len(text_message))
    
    # 3. Final message send karein
    payload = {
        "session": SESSION_NAME,
        "chatId": chat_id,
        "text": text_message
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{WAHA_URL}/api/sendText", json=payload, headers=headers)
        if response.status_code in [200, 201]:
            print(f"✅ Securely sent reply to {phone_number}")
        else:
            print(f"❌ Failed to send: {response.text}")


# import os
# import asyncio
# import uvicorn
# from contextlib import asynccontextmanager
# from fastapi import FastAPI, Request, HTTPException
# from dotenv import load_dotenv

# # Import the actual engine
# from core.worker_pool import start_engine, enqueue_message

# load_dotenv(dotenv_path="config/.env")

# # Startup and shutdown events
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Startup
#     print("🚀 System Starting: Initializing Worker Pool...")
#     await start_engine(num_workers=500)
#     print("⚙️ Powering up system Engine with 500 asynchronous workers...")
#     yield
#     # Shutdown
#     print("🛑 System Shutting Down...")

# app = FastAPI(
#     title="WhatsApp AI Bot System (WAHA QR Edition)",
#     description="High-Concurrency WAHA Webhook Server",
#     version="2.0.0",
#     lifespan=lifespan
# )

# @app.get("/webhook")
# async def verify_webhook():
#     """
#     Since we are not using Meta anymore, this is just a dummy endpoint.
#     WAHA doesn't need GET verification.
#     """
#     return {"status": "WAHA Webhook Ready"}

# @app.post("/webhook")
# async def receive_whatsapp_message(request: Request):
#     """
#     Main Message Reception Endpoint for WAHA
#     CRITICAL: Return 200 OK immediately
#     """
#     try:
#         body = await request.json()
        
#         # WAHA sends events, we only care about new messages
#         event = body.get("event")
        
#         if event == "message":
#             payload = body.get("payload", {})
            
#             # IMPORTANT: Ignore messages sent BY the bot itself
#             if payload.get("fromMe") == True:
#                 return {"status": "success", "message": "Ignored self message"}
            
#             # Extract number (WAHA sends it as 1234567890@c.us)
#             raw_from = payload.get("from", "")
#             phone_number = raw_from.split("@")[0]
            
#             msg_body = payload.get("body", "")
#             msg_type = payload.get("type", "unknown")
            
#             print(f"📥 Message received via WAHA from: +{phone_number}")
#             print(f"   Full message: {msg_body}")
            
#             # ✅ GENIUS TRICK: Reconstruct the old Meta format so your 
#             # base_provider and NLP engine don't break! 
#             meta_style_message = {
#                 "type": "text",
#                 "text": {"body": msg_body}
#             }
            
#             # Enqueue for background processing
#             await enqueue_message(phone_number, meta_style_message)
            
#         return {"status": "success"}
        
#     except Exception as e:
#         print(f"❌ Error in WAHA webhook POST: {e}")
#         import traceback
#         traceback.print_exc()
#         return {"status": "success", "error": str(e)}

# @app.get("/healthz")
# async def health_check():
#     """Health check endpoint for monitoring"""
#     print("✅ Health check called")
#     return {"status": "healthy"}

# @app.get("/")
# async def root():
#     """Root endpoint"""
#     return {"message": "WhatsApp AI Bot System is running with WAHA", "status": "online"}

# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info", workers=1, loop="uvloop", limit_concurrency=1000, timeout_keep_alive=30)