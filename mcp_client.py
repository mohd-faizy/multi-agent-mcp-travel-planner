###################################
# Imports & Configuration
###################################

import os
import sys
import asyncio

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv(override=True)

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
AVIATION_STACK_API_KEY = os.getenv("AVIATIONSTACK_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")


###################################
# MCP Client Initialization
###################################
client = MultiServerMCPClient(
    {
        "tavily": {
            "transport": "streamable_http",
            "url": f"https://mcp.tavily.com/mcp/?tavilyApiKey={TAVILY_API_KEY}",
        },
        "aviationstack": {
            "transport": "stdio",
            "command": sys.executable,
            "args": ["-m", "aviationstack_mcp", "mcp", "run"],
            "env": {"AVIATION_STACK_API_KEY": AVIATION_STACK_API_KEY},
        },
        "weather": {
            "transport": "stdio",
            "command": sys.executable,
            "args": [
                os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    "mcp_servers",
                    "custom_weather_mcp_server.py",
                )
            ],
            "env": {"OPENWEATHER_API_KEY": OPENWEATHER_API_KEY},
        },
    }
)


###################################
# Global Tool References
###################################
search_tool = None
aviation_tools = {}


async def initialize_mcp():
    """Lazily discover and cache MCP tools on first call."""
    global search_tool
    global aviation_tools

    if search_tool is not None and aviation_tools:
        return

    tools = await client.get_tools()

    print("\nAvailable MCP Tools:\n")
    for tool in tools:
        print(tool.name)

    search_tool = next(tool for tool in tools if tool.name == "tavily_search")
    aviation_tools = {tool.name: tool for tool in tools if tool.name != "tavily_search"}


###################################
# Tavily Search
###################################
async def tavily_mcp_search(query: str):
    """Search hotels / destinations via Tavily MCP."""
    await initialize_mcp()
    result = await search_tool.ainvoke({"query": query})
    return result


###################################
# Aviation Stack
###################################
async def aviation_mcp_call(tool_name: str, tool_args: dict = None):
    """Call any AviationStack MCP tool by name."""
    tools = await client.get_tools()
    tool = next(t for t in tools if t.name == tool_name)
    result = await tool.ainvoke(tool_args or {})
    return result


async def get_airports():
    """List airports via the cached aviation MCP tool."""
    await initialize_mcp()
    tool = aviation_tools.get("list_airports")
    if not tool:
        return "Airport tool unavailable"
    result = await tool.ainvoke({})
    return result


async def get_airlines():
    """List airlines via the cached aviation MCP tool."""
    await initialize_mcp()
    tool = aviation_tools.get("list_airlines")
    if not tool:
        return "Airline tool unavailable"
    result = await tool.ainvoke({})
    return result


###################################
# OpenWeather
###################################
weather_tool = None
forecast_tool = None


async def initialize_weather_tools():
    """Lazily discover and cache weather MCP tools."""
    global weather_tool, forecast_tool
    if weather_tool is not None:
        return
    tools = await client.get_tools()
    weather_tool = next(t for t in tools if t.name == "get_current_weather")
    forecast_tool = next(t for t in tools if t.name == "get_forecast")


async def weather_mcp_search(city: str):
    """Fetch current weather for a city."""
    await initialize_weather_tools()
    return await weather_tool.ainvoke({"city": city})


async def forecast_mcp_search(city: str):
    """Fetch weather forecast for a city."""
    await initialize_weather_tools()
    return await forecast_tool.ainvoke({"city": city})


###################################
# Destination Extractor (LLM)
###################################
llm = ChatGroq(model="llama-3.3-70b-versatile")


def extract_destination(query: str):
    """Use the LLM to extract a destination city/country from a travel query."""
    prompt = f"""
    Extract only the destination city or country.

    Query:
    {query}

    Return only destination name.
    """
    response = llm.invoke(prompt)
    return response.content.strip()


###################################
# Entry Point (for standalone testing)
###################################
if __name__ == "__main__":

    async def main():
        tools = await client.get_tools()
        print("\nAvailable Tools:\n")
        for tool in tools:
            print(tool.name)

    asyncio.run(main())
