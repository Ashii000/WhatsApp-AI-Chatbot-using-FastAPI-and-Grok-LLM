import asyncio
import time

class RateLimiter:
    """
    Prevents API rate limit bans by enforcing delays between requests.
    Two separate limiters: one for AI API, one for Meta WhatsApp API.
    """
    
    def __init__(self, requests_per_second: int = 20):
        self.requests_per_second = requests_per_second
        self.min_interval = 1.0 / requests_per_second
        self.last_request_time = 0
        self.lock = asyncio.Lock()
    
    async def wait(self):
        """
        Waits if necessary to maintain the rate limit.
        Non-blocking - multiple callers can wait simultaneously.
        """
        async with self.lock:
            now = time.time()
            time_since_last = now - self.last_request_time
            
            if time_since_last < self.min_interval:
                wait_time = self.min_interval - time_since_last
                print(f"⏱️ Rate limiting: waiting {wait_time:.3f}s")
                await asyncio.sleep(wait_time)
            
            self.last_request_time = time.time()


# Global instances used throughout the system
ai_limiter = RateLimiter(requests_per_second=5)      # AI API rate limit (increased for 500+ users)
meta_limiter = RateLimiter(requests_per_second=0.5)   # Meta API rate limit (increased for 500+ users)