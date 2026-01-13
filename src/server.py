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
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

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

            # 挂载静态文件
            static_path = os.path.join(os.path.dirname(__file__), "..", "static")
            # 挂载context-manager静态资源
            context_manager_path = os.path.join(static_path, "context-manager")
            print(f"Context manager path: {context_manager_path} exists: {os.path.exists(context_manager_path)}")

            @app.get("/")
            async def index(request: Request):
                """主页面 - 支持 SPA 路由"""
                index_path = os.path.join(context_manager_path, "index.html")
                if os.path.exists(index_path):
                    return FileResponse(index_path)
                return {"status": "ok", "service": "Task-Plan MCP Server", "transport": "sse"}

            @app.get("/context-manager{path:path}")
            async def context_manager_handler(request: Request, path: str):
                """Context Manager 路由 - 支持 SPA 和静态文件"""
                full_path = os.path.join(context_manager_path, path.lstrip('/'))                    
                if os.path.exists(full_path) and os.path.isfile(full_path):
                    return FileResponse(full_path)
                else:
                    index_path = os.path.join(context_manager_path, "index.html")
                    if os.path.exists(index_path):
                        return FileResponse(index_path)
                return {"status": "error", "message": "Not found", "path": path}

            @app.get("/health")
            async def health_check():
                """健康检查端点，用于心跳检查"""
                return {"status": "ok", "service": "Task-Plan MCP Server", "transport": "sse"}

            @app.get("/sse")
            async def sse_endpoint(request: Request):
                """SSE 端点"""
                return await handle_sse(request)

            # Context API 端点
            @app.get("/api/contexts")
            async def list_contexts():
                """列出所有上下文"""
                try:
                    contexts = self.tool_call_handler.memory_manager.list_contexts()
                    return {"contexts": [ctx.model_dump() for ctx in contexts]}
                except Exception as e:
                    return {"error": str(e), "contexts": []}

            @app.get("/api/contexts/{context_id}")
            async def get_context(context_id: str):
                """获取上下文详情"""
                try:
                    config = self.tool_call_handler.memory_manager.get_context(context_id)
                    tools = self.tool_call_handler.tool_registry.list_tools(context_id)
                    if config:
                        context_data = config.model_dump()
                        context_data["tools"] = tools
                        return context_data
                    return {"error": "Context not found", "context_id": context_id}
                except Exception as e:
                    return {"error": str(e)}

            @app.get("/api/contexts/{context_id}/memory")
            async def get_combined_memory(context_id: str, query: str, summarize: bool = False):
                """获取组合的memory（personal + task + tool）"""
                try:
                    memory = await self.tool_call_handler.memory_manager.get_combined_memory(
                        context_id, query, summarize
                    )
                    return memory
                except Exception as e:
                    return {"error": str(e)}

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
    
