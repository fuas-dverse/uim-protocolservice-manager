"""
Simple test script for the Chatbot Agent.

Tests the HTTP interface locally.
"""
import httpx
import asyncio
import json


async def test_chatbot_http():
    """Test the chatbot via HTTP endpoint"""
    
    print("=" * 70)
    print("Testing DVerse Chatbot Agent")
    print("=" * 70)
    
    base_url = "http://localhost:8001"
    
    # Test 1: Health check
    print("\n1️⃣ Testing health check...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{base_url}/")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {json.dumps(response.json(), indent=2)}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            print("   Make sure the chatbot service is running!")
            return
    
    # Test 2: Simple query
    print("\n2️⃣ Testing chat query...")
    query = {
        "user_id": "test-user-001",
        "message": "Find recent papers about multi-agent systems",
        "context": {}
    }
    
    print(f"   Query: {query['message']}")
    
    async with httpx.AsyncClient(timeout=180.0) as client:  # 3 minutes for slow LLM
        try:
            response = await client.post(
                f"{base_url}/chat",
                json=query
            )

            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Success!")
                print(f"\n   Chatbot Response:")
                print(f"   {result['message'][:200]}...")
                print(f"\n   Services Discovered: {result['services_discovered']}")

                if result.get('service_invocation'):
                    inv = result['service_invocation']
                    print(f"   Service Used: {inv['service_name']} - {inv['intent_name']}")
                    if inv['data']:
                        papers = inv['data'].get('papers', [])
                        print(f"   Papers Found: {len(papers)}")
            else:
                print(f"   ❌ Error: {response.status_code}")
                print(f"   {response.text}")

        except httpx.ReadTimeout:
            print(f"   ⏱️  Timeout! Agent took longer than 180 seconds.")
            print(f"   Check the chatbot logs - it might have succeeded!")
        except Exception as e:
            print(f"   ❌ Error: {type(e).__name__}: {e}")

    print("\n" + "=" * 70)
    print("Test complete!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_chatbot_http())