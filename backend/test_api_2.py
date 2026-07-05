import httpx
import asyncio

async def main():
    async with httpx.AsyncClient() as client:
        try:
            url = "http://127.0.0.1:8000/api/v1/chat/"
            headers = {"X-Tenant-Id": "tenant-123", "Content-Type": "application/json"}
            payload = {"query": "What is the capital of France?", "user_id": "test_user"}
            async with client.stream("POST", url, headers=headers, json=payload, timeout=60.0) as response:
                print(f"Status Code: {response.status_code}")
                async for chunk in response.aiter_text():
                    print(chunk, end="")
            print("\nStream finished.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
