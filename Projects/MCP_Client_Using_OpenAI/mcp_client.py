import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client
from openai import OpenAI
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

client = OpenAI()


# Fetch tools from SSE servers
async def list_sse_tools(sse_server_map):
    tool_map = {}
    consolidated_tools = []
    for server_name, url in sse_server_map.items():
        async with sse_client(url=url) as streams:
            async with ClientSession(*streams) as session:
                await session.initialize()
                tools = await session.list_tools()
                tool_map.update({tool.name: server_name for tool in tools.tools})
                consolidated_tools.extend(tools.tools)
    return tool_map, consolidated_tools


# Fetch tools from stdio servers
async def list_stdio_tools(stdio_server_map):
    tool_map = {}
    consolidated_tools = []
    for server_name, params in stdio_server_map.items():
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                tool_map.update({tool.name: server_name for tool in tools.tools})
                consolidated_tools.extend(tools.tools)
    return tool_map, consolidated_tools


# Consolidate tools from both SSE and stdio servers
async def list_all_tools(stdio_server_map, sse_server_map):
    sse_tool_map, sse_tools = await list_sse_tools(sse_server_map)
    stdio_tool_map, stdio_tools = await list_stdio_tools(stdio_server_map)
    consolidated_tools = sse_tools + stdio_tools
    tool_map = {**sse_tool_map, **stdio_tool_map}
    return tool_map, consolidated_tools


# Call a specific tool based on its name and arguments
async def call_tool(tool_name, arguments, tool_map, stdio_server_map, sse_server_map):
    server_name = tool_map.get(tool_name)
    if not server_name:
        print(f"Tool '{tool_name}' not found.")
        return

    if server_name in sse_server_map:
        url = sse_server_map[server_name]
        async with sse_client(url=url) as streams:
            async with ClientSession(*streams) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments=arguments)
                return result.content[0].text

    elif server_name in stdio_server_map:
        params = stdio_server_map[server_name]
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments=arguments)
                return result.content[0].text


# Chat function to handle interactions and tool calls
async def chat(
    input_messages,
    tool_map,
    tools=[],
    max_turns=10,
    stdio_server_map=None,
    sse_server_map=None,
):
    chat_messages = input_messages[:]
    for _ in range(max_turns):
        result = client.chat.completions.create(
            model="gpt-4o",
            messages=chat_messages,
            tools=tools,
        )

        if result.choices[0].finish_reason == "tool_calls":
            chat_messages.append(result.choices[0].message)

            for tool_call in result.choices[0].message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                # Log tool call
                log_message = f"**Tool Call**  \n**Tool Name:** `{tool_name}`  \n**Input:**  \n```json\n{json.dumps(tool_args, indent=2)}\n```"
                yield {"role": "assistant", "content": log_message}

                # Call the tool and log its observation
                observation = await call_tool(
                    tool_name, tool_args, tool_map, stdio_server_map, sse_server_map
                )
                log_message = f"**Tool Observation**  \n**Tool Name:** `{tool_name}`  \n**Output:**  \n```json\n{json.dumps(observation, indent=2)}\n```  \n---"
                yield {"role": "assistant", "content": log_message}

                chat_messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(observation),
                    }
                )
        else:
            yield {"role": "assistant", "content": result.choices[0].message.content}
            return

    # Generate a final response if max turns are reached
    result = client.chat.completions.create(
        model="gpt-4o",
        messages=chat_messages,
    )
    yield {"role": "assistant", "content": result.choices[0].message.content}


# Filter and validate input schema for tools
def filter_input_schema(input_schema):
    if "properties" in input_schema:
        if "required" not in input_schema or not isinstance(
            input_schema["required"], list
        ):
            input_schema["required"] = list(input_schema["properties"].keys())
        else:
            for key in input_schema["properties"].keys():
                if key not in input_schema["required"]:
                    input_schema["required"].append(key)

        for key, value in input_schema["properties"].items():
            if "default" in value:
                del value["default"]

        if "additionalProperties" not in input_schema:
            input_schema["additionalProperties"] = False

    return input_schema


if __name__ == "__main__":
    # Define stdio and SSE server configurations
    stdio_server_map = {
        "filesystem_mcp": StdioServerParameters(
            command="npx",
            args=[
                "-y",
                "@modelcontextprotocol/server-filesystem",
                "/path/to/your/filesystem",
            ],
            env=None,
        ),
    }

    sse_server_map = {
        "python_executor_mcp": "ws://localhost:8090/sse",
    }

    # Fetch tools and start chat
    tool_map, tool_objects = asyncio.run(
        list_all_tools(stdio_server_map, sse_server_map)
    )

    tools_json = [
        {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "strict": True,
                "parameters": filter_input_schema(tool.inputSchema),
            },
        }
        for tool in tool_objects
    ]

    input_messages = [
        {
            "role": "system",
            "content": "You can use one tool at a time and keep using tools until you reach the final objective.",
        },
        {"role": "user", "content": "which directory you have access to?"},
    ]

    async def run_chat():
        async for response in chat(
            input_messages,
            tool_map,
            tools=tools_json,
            stdio_server_map=stdio_server_map,
            sse_server_map=sse_server_map,
        ):
            print(response)

    asyncio.run(run_chat())
