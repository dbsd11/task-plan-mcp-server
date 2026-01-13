"""工具调用处理器 - 处理MCP工具调用逻辑"""
import asyncio
from typing import Any, Dict, List
from mcp.types import Tool

ServerMCPTools = [
    Tool(
        name="create_context",
        description="Create a new planning context for isolating memory and planning, with optional tool registration and entity memory setup",
        inputSchema={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Context name"},
                "description": {"type": "string", "description": "Context description (optional)"},
                "parent_context_id": {"type": ["string", "null"], "description": "Parent context ID for creating hierarchical context relationship (optional)", "nullable": True},
                "agent": {
                    "type": "object",
                    "description": "Current Agent information",
                    "properties": {
                        "name": {"type": "string", "description": "Agent name"},
                        "role": {"type": "string", "description": "Agent role"},
                        "terminal_user": {"type": ["string", "null"], "description": "Terminal user information"},
                        "terminal_type": {"type": ["string", "null"], "description": "Terminal type (powershell, cmd, bash, sh)"},
                        "environment": {
                            "type": "object",
                            "description": "Terminal environment information (e.g., Java, Python, Node.js versions)",
                            "properties": {
                                "java_version": {"type": ["string", "null"], "description": "Java version"},
                                "python_version": {"type": ["string", "null"], "description": "Python version"},
                                "nodejs_version": {"type": ["string", "null"], "description": "Node.js version"},
                            },
                        },
                    },
                    "required": ["name", "role"],
                },
            },
            "required": ["name"],
        },
    ),
    Tool(
        name="save_important_plan_feedback_memory",
        description="Save important plan feedback memory with conversation history for a context",
        inputSchema={
            "type": "object",
            "properties": {
                "context_id": {"type": "string", "description": "Context ID"},
                "plan_id": {"type": "string", "description": "Plan ID"},
                "messages": {
                    "type": "array",
                    "description": "List of plan and plan feedback conversation messages",
                    "items": {
                        "type": "object",
                        "properties": {
                            "role": {"type": "string", "enum": ["user", "assistant"]},
                            "content": {"type": "string"},
                        },
                        "required": ["role", "content"],
                    },
                },
                "metadata": {"type": "object", "description": "Optional metadata"},
            },
            "required": ["context_id", "plan_id", "messages"],
        },
    ),
    Tool(
        name="compress_history_messages",
        description="compress working memory and get compressed context history",
        inputSchema={
            "type": "object",
            "properties": {
                "context_id": {"type": "string", "description": "Context ID"},
                "messages": {
                    "type": "array",
                    "description": "List of messages to compress",
                    "items": {
                        "type": "object",
                        "properties": {
                            "role": {"type": "string", "enum": ["user", "assistant", "tool"]},
                            "content": {"type": "string"},
                        },
                        "required": ["role", "content"],
                    },
                },
                "working_summary_mode": {"type": "string", "enum": ["auto", "manual"], "description": "Compression mode", "default": "auto"},
                "compact_ratio_threshold": {"type": "number", "description": "Compression ratio threshold", "default": 0.75},
                "max_total_tokens": {"type": "integer", "description": "Max total tokens", "default": 20000},
                "max_tool_message_tokens": {"type": "integer", "description": "Max tool message tokens", "default": 2000},
                "keep_recent_count": {"type": "integer", "description": "Number of recent messages to keep", "default": 1},
                "metadata": {"type": "object", "description": "Optional metadata"},
            },
            "required": ["context_id", "messages"],
        },
    ),
    Tool(
        name="save_tool_execution_feedback_memory",
        description="save tool execution feedback",
        inputSchema={
            "type": "object",
            "properties": {
                "context_id": {"type": "string", "description": "Context ID"},
                "plan_id": {"type": "string", "description": "Original plan ID"},
                "execution_feedback": {
                    "type": "array",
                    "description": "Feedback from execution",
                    "items": {
                        "type": "object",
                        "properties": {
                            "step_id": {"type": ["string", "null"], "description": "Step ID", "nullable": True},
                            "tool_name": {"type": "string"},
                            "domain": {"type": ["string", "null"], "nullable": True},
                            "success": {"type": "boolean"},
                            "input": {"nullable": True},
                            "output": {"nullable": True},
                            "error": {"type": ["string", "null"], "nullable": True},
                            "create_time": {"type": ["string", "null"], "nullable": True},
                            "execution_time": {"type": "number", "nullable": True},
                            "token_cost": {"type": "integer", "nullable": True},
                        },                                                                                                                                                                                                                                        
                        "required": ["tool_name", "success"],
                    },
                },
            },
            "required": ["context_id", "plan_id", "execution_feedback"],
        },
    ),
    Tool(
        name="plan_tool_calls",
        description="Dynamically plan tool calls for a query within a context",
        inputSchema={
            "type": "object",
            "properties": {
                "context_id": {"type": "string", "description": "Context ID"},
                "query": {"type": "string", "description": "User query to plan for"},
                "tools": {
                    "type": "array",
                    "description": "List of tool definitions for dynamic planning (optional)",
                    "items": {
                        "type": "object",
                        "properties": {
                            "domain": {"type": "string"},
                            "tool_name": {"type": "string"},
                            "description": {"type": "string"},
                            "args": {"type": "object"},
                            "input": {"type": "object"},
                            "output": {"type": "object"},
                        },
                        "required": ["domain", "tool_name", "description"],
                    },
                },
            },
            "required": ["context_id", "query"],
        },
    ),
    Tool(
        name="query_combined_memory",
        description="Get combined personal and task memory for a context",
        inputSchema={
            "type": "object",
            "properties": {
                "context_id": {"type": "string", "description": "Context ID"},
                "query": {"type": "string", "description": "Query to retrieve relevant memories"},
            },
            "required": ["context_id", "query"],
        },
    ),
]

import os

from .memory import MemoryManager
from .types import (
    ToolDefinition,
    Plan,
    PlanExecutionResult,
)

from .planner import ToolPlanner, DynamicPlanAdjuster

from .tools import ToolRegistry

class ToolCallHandler:
    """工具调用处理器"""
    
    def __init__(
        self,
    ):
        self.llm_model = os.getenv("FLOW_LLM_MODEL", "qwen3-30b-a3b-thinking-2507")
        self.embedding_model = os.getenv("FLOW_EMBEDDING_MODEL", "text-embedding-v4")
        self.tool_registry = ToolRegistry()
        self.memory_manager = MemoryManager(self.llm_model, self.embedding_model, tool_registry=self.tool_registry)
        self.tool_planner = ToolPlanner(self.memory_manager, self.tool_registry)
        self.plan_adjuster = DynamicPlanAdjuster(self.memory_manager)
        self._context_plans: Dict[str, Plan] = {}
        # 初始化异步队列用于后台处理工具调用，设置最大容量
        self._tool_call_queue: asyncio.Queue = asyncio.Queue(maxsize=1000)  # 设置队列最大容量为1000
        # 初始化后台任务为None，延迟到第一次调用异步方法时创建
        self._background_task = None
    
    def _get_context_plans(self, context_id: str) -> Dict[str, Plan]:
        """获取context的计划字典"""
        if context_id not in self._context_plans:
            self._context_plans[context_id] = {}
        return self._context_plans[context_id]
    
    async def _process_tool_call_queue(self) -> None:
        """后台处理工具调用队列"""
        while True:
            try:
                # 从队列中获取工具调用请求
                tool_call = await self._tool_call_queue.get()
                name = tool_call["name"]
                arguments = tool_call["arguments"]
                
                # 处理工具调用（这部分是原有的同步处理逻辑）
                if name == "save_important_plan_feedback_memory":
                    await self.memory_manager.save_plan_feedback_memory(
                        arguments["context_id"],
                        arguments["plan_id"],
                        arguments["messages"],
                        arguments.get("metadata"),
                    )
                
                elif name == "save_tool_execution_feedback_memory":
                    context_id = arguments["context_id"]
                    plan_id = arguments["plan_id"]
                    feedback = arguments["execution_feedback"]
                    
                    results = []
                    for f in feedback:
                        from datetime import datetime
                        results.append(PlanExecutionResult(
                            plan_id=plan_id,
                            context_id=context_id,
                            step_id=f.get("step_id", ""),
                            tool_name=f.get("tool_name", ""),
                            domain=f.get("domain", ""),
                            success=f["success"],
                            input=f.get("input"),
                            output=f.get("output"),
                            error=f.get("error"),
                            create_time=f.get("create_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                            execution_time=f.get("execution_time", 0.0),
                            token_cost=f.get("token_cost", 0),
                        ))
                    
                    # 先从执行结果中学习
                    for result in results:
                        if result.tool_name:
                            # 检查工具是否已在registry中注册，如未注册则自动注册
                            if not self.tool_registry.has_tool(result.tool_name, result.domain, context_id):
                                # 创建并注册ToolDefinition
                                tool_def = ToolDefinition(
                                    domain=result.domain,
                                    tool_name=result.tool_name,
                                    description=f"Auto-registered tool from execution: {result.tool_name}",
                                    args={},
                                    output={}
                                )
                                self.tool_registry.register(tool_def, context_id)
                            
                            # 调用learn_from_execution方法记录工具执行结果
                            await self.plan_adjuster.learn_from_execution(
                                context_id=context_id,
                                tool_name=result.tool_name,
                                success=result.success,
                                input_data=result.input,
                                output_data=result.output,
                                create_time=result.create_time,
                                execution_time=result.execution_time,
                                token_cost=result.token_cost,
                            )
                
                elif name == "compress_history_messages":
                    await self.memory_manager.write_working_memory(
                        arguments["context_id"],
                        arguments["messages"],
                        keep_recent_count=arguments.get("keep_recent_count", 2),
                        metadata=arguments.get("metadata"),
                    )
            except Exception as e:
                # 捕获并记录异常，防止后台任务崩溃
                print(f"Error processing tool call {name}: {str(e)}")
            finally:
                # 标记任务完成
                self._tool_call_queue.task_done()
    
    async def handle_tool_call(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """处理工具调用"""
        
        # 延迟创建后台任务，确保事件循环已经运行
        if self._background_task is None:
            self._background_task = asyncio.create_task(self._process_tool_call_queue())
        
        # 对于plan_tool_calls、get_combined_memory和create_context，直接同步处理
        if name == "create_context":
            agent_info = None
            if "agent" in arguments and arguments["agent"]:
                agent_info = arguments["agent"]

            config = self.memory_manager.create_context(
                name=arguments.get("name", ""),
                description=arguments.get("description", ""),
                agent_info=agent_info,
                parent_context_id=arguments.get("parent_context_id"),
            )
            context_id = config.context_id
        
            # Handle agent memory setup if provided
            agent_result = None
            if agent_info:
                env_info = agent_info.get("environment", {})
                env_str = ", ".join([f"{k.replace('_version', '')}: {v}" for k, v in env_info.items() if v]) if env_info else None
                content_parts = [
                    f"Agent Name: {agent_info.get('name', 'N/A')}",
                    f"Agent Role: {agent_info.get('role', 'N/A')}",
                    f"Terminal User: {agent_info.get('terminal_user', 'N/A')}",
                    f"Terminal Type: {agent_info.get('terminal_type', 'N/A')}",
                    f"Environment: {env_str if env_str else 'N/A'}",
                ]
                agent_content = "\n".join(content_parts)
                agent_result = await self.memory_manager.set_personal_memory(
                    context_id,
                    [{"role": "assistant", "content": agent_content}],
                    arguments.get("metadata"),
                )
            
            result = {
                "success": True,
                "context_id": context_id,
                "name": config.name,
                "description": config.description,
                "created_at": config.created_at
            }

            if agent_result:
                result["agent_memory_result"] = agent_result.model_dump()

            return result
            
        elif name == "plan_tool_calls":
            context_id = arguments["context_id"]
            query = arguments["query"]
            context_plans = self._get_context_plans(context_id)
            
            # 动态工具定义支持
            temp_tools = []
            if "tools" in arguments and arguments["tools"]:
                for t in arguments["tools"]:
                    temp_tools.append(ToolDefinition(
                        domain=t["domain"],
                        tool_name=t["tool_name"],
                        description=t["description"],
                        args=t.get("args", {}),
                        input=t.get("input", {}),
                        output=t.get("output", {})
                    ))
                self.tool_registry.register_batch(temp_tools, context_id)
            
            plan = await self.tool_planner.plan(context_id, query)
            context_plans[plan.plan_id] = plan
            return {
                "success": True,
                "plan_id": plan.plan_id,
                "context_id": plan.context_id,
                "query": plan.query,
                "steps": [s.model_dump() for s in plan.steps],
                "context": plan.context,
                "created_at": plan.created_at,
            }

        elif name == "query_combined_memory":
            combined = await self.memory_manager.get_combined_memory(
                arguments["context_id"],
                arguments["query"],
                True,
            )
            return {"success": True, "context_id": arguments["context_id"], "query": arguments["query"], **combined}
        
        # 其他所有工具调用，放入异步队列处理，直接返回success
        else:
            # 检查队列是否已满，如果未满则放入队列，否则丢弃
            self._tool_call_queue.put_nowait({
                "name": name,
                "arguments": arguments
            })
            # 直接返回success：True
            return {"success": True}