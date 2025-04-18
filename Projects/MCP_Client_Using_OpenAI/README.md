# MCP Client Using OpenAI

MCP Client Using OpenAI is a tool designed to interact with Model Context Protocol (MCP) servers using OpenAI's language models. It allows users to list available tools, call them, and engage in interactive chats to achieve specific objectives.

## File Descriptions
- **mcp_client.py**: Contains the core logic for interacting with MCP servers (both SSE and stdio), listing tools, and calling them.
- **main.py**: The entry point for the Streamlit app, providing a user-friendly interface for interacting with MCP servers and tools.

## Running the Application
To run the Streamlit app, execute the following command in the terminal:
```bash
streamlit run main.py
```

## MCP Servers Used
This project interacts with the following MCP servers:
- [Pydantic AI MCP Server](https://github.com/pydantic/pydantic-ai/tree/main/mcp-run-python)
- [Filesystem MCP Server](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem)
- [Time MCP Server](https://github.com/modelcontextprotocol/servers/tree/main/src/time)

## Video Demo
Watch the demo full walkthrough of this project here: https://youtu.be/eZqzSeVBBDw