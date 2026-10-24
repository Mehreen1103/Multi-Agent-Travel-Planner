import os
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio

load_dotenv()

# Safely fetch the API key
api_key = os.getenv("AVIATION_STACK_API_KEY") or os.getenv("AVIATIONSTACK_API_KEY")

# Build the env dictionary, but ONLY include keys that actually have a value (not None)
server_env = {}
if api_key:
    server_env["AVIATION_STACK_API_KEY"] = api_key
else:
    print("⚠️ Warning: AVIATION_STACK_API_KEY not found in environment variables!")

client = MultiServerMCPClient(
    {
        "aviationstack": {
            "transport": "stdio",
            "command": r"C:\Users\Dynamic_Computer\Desktop\multi-agent-with-mcp\aviationstack-mcp\.venv\Scripts\python.exe",
            "args": [
                "-m",
                "aviationstack_mcp",
                "mcp",
                "run"
            ],
            "env": server_env  # This will only pass valid strings or be empty
        }
    }
)

async def main():
    tools = await client.get_tools()

    print("\nAvailable Tools:\n")
    for tool in tools:
        print(tool.name)

if __name__ == "__main__":
    asyncio.run(main())