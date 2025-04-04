import asyncio
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client
from openai import OpenAI
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

client = OpenAI()


class ConnectionManager:
    def __init__(self, stdio_server_map, sse_server_map):
        self.stdio_server_map = stdio_server_map
        self.sse_server_map = sse_server_map
        self.sessions = {}
        self.exit_stack = AsyncExitStack()

    async def initialize(self):
        # Initialize stdio connections
        for server_name, params in self.stdio_server_map.items():
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(params)
            )
            read, write = stdio_transport
            session = await self.exit_stack.enter_async_context(
                ClientSession(read, write)
            )
            await session.initialize()
            self.sessions[server_name] = session

        # Initialize SSE connections
        for server_name, url in self.sse_server_map.items():
            sse_transport = await self.exit_stack.enter_async_context(
                sse_client(url=url)
            )
            read, write = sse_transport
            session = await self.exit_stack.enter_async_context(
                ClientSession(read, write)
            )
            await session.initialize()
            self.sessions[server_name] = session

    async def list_tools(self):
        tool_map = {}
        consolidated_tools = []
        for server_name, session in self.sessions.items():
            tools = await session.list_tools()
            tool_map.update({tool.name: server_name for tool in tools.tools})
            consolidated_tools.extend(tools.tools)
        return tool_map, consolidated_tools

    async def call_tool(self, tool_name, arguments, tool_map):
        server_name = tool_map.get(tool_name)
        if not server_name:
            print(f"Tool '{tool_name}' not found.")
            return

        session = self.sessions.get(server_name)
        if session:
            result = await session.call_tool(tool_name, arguments=arguments)
            return result.content[0].text

    async def close(self):
        await self.exit_stack.aclose()


# Chat function to handle interactions and tool calls
async def chat(
    input_messages,
    tool_map,
    tools=[],
    max_turns=10,
    connection_manager=None,
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
                observation = await connection_manager.call_tool(
                    tool_name, tool_args, tool_map
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

    async def main():
        connection_manager = ConnectionManager(stdio_server_map, sse_server_map)
        await connection_manager.initialize()

        tool_map, tool_objects = await connection_manager.list_tools()

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

        async for response in chat(
            input_messages,
            tool_map,
            tools=tools_json,
            connection_manager=connection_manager,
        ):
            print(response)

        await connection_manager.close()

    asyncio.run(main())
