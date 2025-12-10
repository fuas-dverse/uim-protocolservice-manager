import httpx
import asyncio
from loguru import logger


async def test_ollama():
    """Test if Ollama is responsive"""
    
    logger.info("Testing Ollama...")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test Ollama API
            response = await client.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "qwen2.5",
                    "prompt": "Say hello in one word",
                    "stream": False
                }
            )
            
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"✅ Ollama response: {data.get('response')}")
            return True
            
    except httpx.TimeoutException:
        logger.error("❌ Ollama timeout - is it running?")
        return False
    except httpx.ConnectError:
        logger.error("❌ Can't connect to Ollama - is it running on port 11434?")
        return False
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    asyncio.run(test_ollama())
