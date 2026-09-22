import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(
    command="python",
    args=["-m", "mcp_server.server"]
)

async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("TOOLS:")
            for tool in tools.tools:
                print(tool.name)

            print("\nWEATHER:")
            result = await session.call_tool(
                "get_weather",
                {"city": "Bangalore"}
            )
            print(result)

            print("\nADVISORY:")
            result = await session.call_tool(
                "get_weather_advisory",
                {
                    "city": "Bangalore",
                    "activity": "cycling"
                }
            )
            print(result)

if __name__ == "__main__":
    asyncio.run(main())