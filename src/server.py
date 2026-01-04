"""Task-Plan MCP Server - 基于ReMe记忆的动态工具规划MCP服务器，支持Context隔离"""

import os
from reme_ai.core.utils import load_env
load_env()

import asyncio
import json
import argparse
from typing import Any, Dict

from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import TextContent

from .tool_call import ServerMCPTools, ToolCallHandler

from fastapi import FastAPI, Request

class TaskPlanMCPServer:
    """Task-Plan MCP服务器 - 支持Context隔离"""

    def __init__(
        self,
    ):
        self.server = Server("task-plan-mcp-server")
        self.tool_call_handler = ToolCallHandler()

        self._setup_handlers()

    def _setup_handlers(self):
        """设置MCP工具处理器"""

        @self.server.list_tools()
        async def list_tools():
            return ServerMCPTools

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]):
            try:
                result = await self.tool_call_handler.handle_tool_call(name, arguments)
                return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
            except Exception as e:
                return [TextContent(type="text", text=json.dumps({"error": str(e)}, ensure_ascii=False, indent=2))]

    def run(self, transport: str = "stdio", port: int = 8080):
        """运行MCP服务器"""
        if transport == "sse":
            sse_transport = SseServerTransport("/messages")
            
            async def handle_sse(request: Request):
                async with sse_transport.connect_sse(
                    request.scope,
                    request.receive,
                    request._send,
                ) as (read_stream, write_stream):
                    await self.server.run(
                        read_stream,
                        write_stream,
                        self.server.create_initialization_options(),
                    )
            
            import uvicorn

            # FastAPI 应用
            app = FastAPI(title="Task-Plan MCP Server", debug=True)

            @app.get("/")
            async def health_check():
                """健康检查端点，用于心跳检查"""
                return {"status": "ok", "service": "Task-Plan MCP Server", "transport": "sse"}

            @app.get("/sse")
            async def sse_endpoint(request: Request):
                """SSE 端点"""
                return await handle_sse(request)

            # 挂载 SSE 消息处理
            app.mount("/messages/", sse_transport.handle_post_message)
            uvicorn.run(app, host='0.0.0.0', port=port)

if __name__ == "__main__":
    """主入口"""
    import argparse

    parser = argparse.ArgumentParser(description="Task-Plan MCP Server")
    parser.add_argument("--transport", default="sse", choices=["sse"], help="Transport type (sse)")
    parser.add_argument("--port", type=int, default=8080, help="Port for Http Api")

    args = parser.parse_args()

    server = TaskPlanMCPServer()
    server.run(transport=args.transport, port=args.port)
    