import streamlit as st
import asyncio
import json
from mcp_client import (
    chat,
    ConnectionManager,
    filter_input_schema,
    StdioServerParameters,
)

# Streamlit app title
st.title("MCP Client")

# Sidebar for configuring MCP servers
st.sidebar.title("MCP Server Configuration")

# Input for stdio servers (JSON format)
stdio_servers = st.sidebar.text_area(
    "Stdio Servers (JSON format)",
    value=json.dumps(
        {
            "filesystem_mcp": {
                "command": "npx",
                "args": [
                    "-y",
                    "@modelcontextprotocol/server-filesystem",
                    "/path/to/your/filesystem",
                ],
                "env": None,
            }
        },
        indent=4,
    ),
)

# Input for SSE servers (JSON format)
sse_servers = st.sidebar.text_area(
    "SSE Servers (JSON format)",
    value=json.dumps(
        {"python_executor_mcp": "ws://localhost:8090/sse"},
        indent=4,
    ),
)

# Parse server configurations and handle invalid JSON
try:
    stdio_server_map = {
        name: StdioServerParameters(**params)
        for name, params in json.loads(stdio_servers).items()
    }
    sse_server_map = json.loads(sse_servers)
except json.JSONDecodeError:
    st.sidebar.error("Invalid JSON format in server configuration.")
    stdio_server_map, sse_server_map = {}, {}

# Initialize chat history if not already present
if "messages" not in st.session_state:
    system_message = "You can use one tool at a time and keep using tools until you reach the final objective."
    st.session_state.messages = [{"role": "system", "content": system_message}]

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Async function to handle chat and stream messages
async def handle_chat(connection_manager):
    # Fetch available tools from configured servers
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

    # Stream responses from the chat function
    async for response in chat(
        st.session_state.messages,
        tool_map,
        tools=tools_json,
        connection_manager=connection_manager,
    ):
        yield response


# React to user input
if user_message := st.chat_input("Your Message"):
    # Display user message in chat container
    st.chat_message("user").markdown(user_message)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_message})

    # Process assistant response
    with st.spinner("Assistant is typing..."):
        response_container = st.chat_message("assistant")

        async def stream_responses():
            # Initialize ConnectionManager
            connection_manager = ConnectionManager(stdio_server_map, sse_server_map)
            await connection_manager.initialize()

            try:
                # Stream assistant responses and update chat history
                async for response in handle_chat(connection_manager):
                    response_container.markdown(response["content"])
                    st.session_state.messages.append(response)
            finally:
                # Ensure connections are closed
                await connection_manager.close()

        asyncio.run(stream_responses())
