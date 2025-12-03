import asyncio
import json
from datetime import datetime
from nats.aio.client import Client as NATS


async def test_agent_query():
    """Simulate an agent sending a query to the AQS"""
    
    print("🤖 Starting test agent...")
    
    # Connect to NATS
    nc = NATS()
    await nc.connect("nats://localhost:4222")
    print("✅ Connected to NATS")
    
    # Create a query message
    query = {
        "agent_id": "test-agent-001",
        "message": "Find me weather services that can provide forecasts",
        "context": {
            "location": "Europe",
            "previous_services": []
        },
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    print(f"\n📤 Sending query: '{query['message']}'")
    
    # Subscribe to response topic first
    response_received = asyncio.Event()
    
    async def response_handler(msg):
        """Handle response from AQS"""
        print("\n📨 Received response:")
        data = json.loads(msg.data.decode())
        print(json.dumps(data, indent=2))
        response_received.set()
    
    await nc.subscribe("uim.catalogue.response", cb=response_handler)
    print("✅ Subscribed to response topic")
    
    # Publish query
    await nc.publish(
        "uim.catalogue.query",
        json.dumps(query).encode()
    )
    print("✅ Query published to uim.catalogue.query")
    
    # Wait for response (timeout after 30 seconds)
    print("\n⏳ Waiting for response...")
    try:
        await asyncio.wait_for(response_received.wait(), timeout=30.0)
        print("\n✅ Test completed successfully!")
    except asyncio.TimeoutError:
        print("\n❌ Timeout waiting for response (30s)")
        print("   Make sure:")
        print("   1. AQS is running (python main.py)")
        print("   2. Catalogue API is running")
        print("   3. NATS is running")
    
    await nc.close()
    print("\n👋 Test agent finished")


async def test_health_check():
    """Test the AQS health check endpoint"""
    
    print("\n🏥 Testing health check...")
    
    nc = NATS()
    await nc.connect("nats://localhost:4222")
    
    response_received = asyncio.Event()
    
    async def health_response_handler(msg):
        print("\n📨 Health check response:")
        data = json.loads(msg.data.decode())
        print(json.dumps(data, indent=2))
        response_received.set()
    
    await nc.subscribe("uim.aqs.health.response", cb=health_response_handler)
    
    # Send health check request
    await nc.publish("uim.aqs.health", b'{}')
    
    try:
        await asyncio.wait_for(response_received.wait(), timeout=5.0)
    except asyncio.TimeoutError:
        print("❌ Health check timeout")
    
    await nc.close()


async def main():
    """Run all tests"""
    print("=" * 60)
    print("AQS Test Suite")
    print("=" * 60)
    
    # Test health check first
    await test_health_check()
    
    print("\n" + "=" * 60)
    
    # Test agent query
    await test_agent_query()
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
