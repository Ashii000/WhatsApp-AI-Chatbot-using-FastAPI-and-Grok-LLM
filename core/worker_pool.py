import asyncio
from core.whatsapp_webhook import send_whatsapp_message
from core.rate_limiter import ai_limiter

# Import our newly built Enterprise Components
from memory_engine.sqlite_manager import SQLiteManager
from storylines.resolver import StorylineResolver
from intelligence.adaptive_learning import AdaptiveLearner
from api_providers.provider_factory import ai_factory

# The High-Concurrency Queue
message_queue = asyncio.Queue()

async def process_user_message(phone_number: str, message_data: dict):
    """
    The main pipeline for a single message.
    Now with comprehensive error handling and logging.
    """
    user_text = message_data.get("text", {}).get("body", "")
    
    if not user_text:
        print(f"⚠️ No text content in message from {phone_number}")
        return

    try:
        print(f"🔄 [START] Processing message from {phone_number}")
        
        # Step 1: Initialize memory
        db = SQLiteManager(phone_number)
        chat_history = await db.get_recent_context()
        await db.save_interaction("user", user_text)
        print(f"   ✅ Memory initialized, history: {len(chat_history)} messages")

        # Step 2: Get learned profile
        learner = AdaptiveLearner(phone_number, db.db_path)
        learned_profile = await learner.get_learned_profile()
        print(f"   ✅ Learned profile retrieved")

        # Step 3: Resolve storyline
        system_prompt = await StorylineResolver.get_system_prompt(phone_number, learned_profile)
        print(f"   ✅ System prompt resolved ({len(system_prompt)} chars)")

        # Step 4: Rate limit
        print(f"   ⏱️ Checking AI rate limit...")
        await ai_limiter.wait()
        print(f"   ✅ Rate limit cleared")

        # Step 5: Generate AI response
        print(f"   🤖 Generating AI response...")
        ai_response = await ai_factory.generate_response(system_prompt, chat_history, user_text)
        
        if not ai_response:
            print(f"   ❌ AI returned empty response!")
            ai_response = "Sorry, I'm having trouble thinking right now. Try again!"
        
        print(f"   ✅ AI response: {ai_response[:100]}...")

        # Step 6: Send to WhatsApp
        print(f"   📤 Sending to WhatsApp...")
        send_result = await send_whatsapp_message(phone_number, ai_response)
        
        if not send_result:
            print(f"   ❌ Failed to send WhatsApp message!")
            return
        
        print(f"   ✅ WhatsApp message sent")

        # Step 7: Save response
        await db.save_interaction("assistant", ai_response)
        print(f"   ✅ Response saved to database")

        # Step 8: Evolve personality (background)
        async def analysis_wrapper(system_prompt_inner, user_text_inner):
            return await ai_factory.generate_response(system_prompt_inner, [], user_text_inner)
        
        asyncio.create_task(learner.evolve_personality(analysis_wrapper))
        print(f"   🧠 Personality evolution task started")
        
        print(f"✅ [SUCCESS] Message from {phone_number} processed completely!")

    except Exception as e:
        print(f"❌ [ERROR] Processing message for {phone_number}: {str(e)}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        
        # Try to send error message to user
        try:
            error_message = "Sorry, I encountered an error. Please try again."
            await send_whatsapp_message(phone_number, error_message)
        except:
            pass

async def background_worker(worker_id: int):
    """Continuously pulls messages from the queue and processes them in parallel."""
    while True:
        phone_number, message_data = await message_queue.get()
        print(f"[Worker-{worker_id}] Handling active session for {phone_number}")
        await process_user_message(phone_number, message_data)
        message_queue.task_done()

async def start_engine(num_workers: int = 500):
    """
    Ignites the worker pool. Setting 500 workers allows the bot to 
    process 500 different users simultaneously without any blocking.
    """
    print(f"⚙️ Powering up system Engine with {num_workers} asynchronous workers...")
    for i in range(num_workers):
        asyncio.create_task(background_worker(i))

async def enqueue_message(phone_number: str, message_data: dict):
    """Entry point used by main.py to quickly offload messages to the background workers."""
    await message_queue.put((phone_number, message_data))