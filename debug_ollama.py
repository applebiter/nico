"""Debug the Ollama API response."""
import asyncio
import aiohttp


async def test_direct():
    """Test Ollama API directly."""
    async with aiohttp.ClientSession() as session:
        # Test 1: Simple generation
        print("Test 1: Simple text generation")
        print("-" * 50)
        payload = {
            "model": "qwen3:4b",
            "prompt": "Complete this name: Captain Elara",
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 20,
            }
        }
        
        async with session.post(
            "http://localhost:11434/api/generate",
            json=payload,
            timeout=aiohttp.ClientTimeout(total=30)
        ) as resp:
            result = await resp.json()
            print(f"Status: {resp.status}")
            print(f"Keys in response: {list(result.keys())}")
            print(f"Response field: '{result.get('response', 'MISSING')}'")
            print(f"Thinking field exists: {'thinking' in result}")
            if 'thinking' in result:
                print(f"Thinking length: {len(result['thinking'])} chars")
            print(f"Full result:\n{result}")


asyncio.run(test_direct())
