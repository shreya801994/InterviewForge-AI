import time
import logging
from functools import wraps
from fastapi import HTTPException, status
from google.genai.errors import APIError

logger = logging.getLogger(__name__)

def retry(max_retries: int = 3, base_delay: int = 1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    error_str = str(e).lower()
                    
                    # 1. Fail fast on Quota / Rate Limits (do not retry)
                    if "429" in error_str or "resource_exhausted" in error_str or "quota" in error_str:
                        logger.error(f"AI Quota/Rate Limit hit. Failing immediately on attempt {attempt + 1}: {e}")
                        raise HTTPException(
                            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                            detail="AI service rate limit exceeded or quota exhausted. Please try again later."
                        )
                        
                    # 2. Do not retry AIParsingError (handled by internal loop in client.py)
                    from app.ai.parser import AIParsingError
                    if isinstance(e, AIParsingError):
                        logger.error(f"AIParsingError caught. Failing without outer retries: {e}")
                        raise HTTPException(
                            status_code=status.HTTP_502_BAD_GATEWAY,
                            detail=f"AI parsing error: {str(e)}"
                        )

                    # Only retry if attempts remain
                    if attempt < max_retries - 1:
                        wait_time = base_delay * (2 ** attempt)
                        logger.warning(
                            f"AI API call failed "
                            f"(attempt {attempt + 1}/{max_retries}), "
                            f"retrying in {wait_time}s: {e}"
                        )
                        time.sleep(wait_time)
            
            # If all retries exhausted for general errors
            logger.error(
                f"AI API call failed after {max_retries} attempts: {last_exception}",
                exc_info=True
            )
            
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"AI service temporarily unavailable: {str(last_exception)}"
            )
        return wrapper
    return decorator
