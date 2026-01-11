"""工具调用处理器 - 处理MCP工具调用逻辑"""
from typing import Any, Dict, List
from mcp.types import Tool

ServerMCPTools = [
    Tool(
        name="create_context",
        description="Create a new planning context for isolating memory and planning, with optional tool registration and entity memory setup",
        inputSchema={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Context name (optional)"},
                "description": {"type": "string", "description": "Context description (optional)"},
                "tools": {
                    "type": "array",
                    "description": "List of tool definitions to register (optional)",
                    "items": {
                        "type": "object",
                        "properties": {
                            "domain": {"type": "string"},
                            "tool_name": {"type": "string"},
                            "description": {"type": "string"},
                            "args": {"type": "object"},
                            "output": {"type": "object"},
                        },
                        "required": ["domain", "tool_name", "description"],
                    },
                },
                "entities": {
                    "type": "array",
                    "description": "List of entity definitions to set (optional)",
                    "items": {
                        "type": "object",
                        "properties": {
                            "entity_id": {"type": "string", "description": "Entity unique identifier"},
                            "entity_type": {"type": "string", "description": "Entity type (e.g., person, project, system)"},
                            "name": {"type": "string", "description": "Entity name"},
                            "description": {"type": "string", "description": "Entity description"},
                            "attributes": {"type": "object", "description": "Entity attributes as key-value pairs"},
                            "relationships": {
                                "type": "array",
                                "description": "Entity relationships",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "target_entity_id": {"type": "string", "description": "Related entity ID"},
                                        "relationship_type": {"type": "string", "description": "Relationship type (e.g., contains, depends_on, related_to)"},
                                        "description": {"type": "string", "description": "Relationship description"},
                                    },
                                    "required": ["target_entity_id", "relationship_type"],
                                },
                            },
                        },
                        "required": ["entity_id", "entity_type", "name"],
                    },
                },
                "metadata": {"type": "object", "description": "Optional metadata for entity memory"},
            },
        },
    ),
    Tool(
        name="save_important_task_memory",
        description="Save important task memory with conversation history for a context",
        inputSchema={
            "type": "object",
            "properties": {
                "context_id": {"type": "string", "description": "Context ID"},
                "task_id": {"type": "string", "description": "Task ID"},
                "messages": {
                    "type": "array",
                    "description": "List of conversation messages",
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
            "required": ["context_id", "task_id", "messages"],
        },
    ),
    Tool(
        name="compress_working_memory",
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
                            "step_id": {"type": "string"},
                            "tool_name": {"type": "string"},
                            "domain": {"type": "string"},
                            "success": {"type": "boolean"},
                            "output": {},
                            "error": {"type": "string"},
                            "execution_time": {"type": "number"},
                        },                                                                                                                                                                                                                                                       
                        "required": ["step_id", "success"],
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
            },
            "required": ["context_id", "query"],
        },
    ),
    Tool(
        name="get_combined_memory",
        description="Get combined personal and task memory for a context",
        inputSchema={
            "type": "object",
            "properties": {
                "context_id": {"type": "string", "description": "Context ID"},
                "query": {"type": "string", "description": "Query to retrieve relevant memories"},
                "summarize": {"type": "boolean", "description": "Whether to get summarized memory", "default": False},
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
        self.memory_manager = MemoryManager(self.llm_model, self.embedding_model)
        self.tool_registry = ToolRegistry()
        self.tool_planner = ToolPlanner(self.memory_manager, self.tool_registry)
        self.plan_adjuster = DynamicPlanAdjuster(self.memory_manager, self.tool_registry)
        self._context_plans: Dict[str, Plan] = {}
    
    def _get_context_plans(self, context_id: str) -> Dict[str, Plan]:
        """获取context的计划字典"""
        if context_id not in self._context_plans:
            self._context_plans[context_id] = {}
        return self._context_plans[context_id]
    
    async def handle_tool_call(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """处理工具调用"""
        
        if name == "create_context":
            config = self.memory_manager.create_context(
                name=arguments.get("name", ""),
                description=arguments.get("description", ""),
            )
            context_id = config.context_id
            
            # Handle tool registration if provided
            tools_registered = 0
            if "tools" in arguments and arguments["tools"]:
                tool_definitions = []
                for t in arguments["tools"]:
                    tool_definitions.append(ToolDefinition(
                        domain=t["domain"],
                        tool_name=t["tool_name"],
                        description=t["description"],
                        args=t.get("args", {}),
                        output=t.get("output", {}),
                    ))
                tools_registered = self.tool_registry.register_batch(tool_definitions, context_id)
            
            # Handle entity memory setup if provided
            entity_result = None
            if "entities" in arguments and arguments["entities"]:
                entity_result = await self.memory_manager.set_entity_memory(
                    context_id,
                    arguments["entities"],
                    arguments.get("metadata"),
                )
            
            result = {
                "success": True,
                "context_id": context_id,
                "name": config.name,
                "description": config.description,
                "created_at": config.created_at,
                "tools_registered": tools_registered,
            }
            
            if entity_result:
                result["entity_memory_result"] = entity_result.model_dump()
            
            return result
        
        elif name == "save_important_task_memory":
            result = await self.memory_manager.set_task_memory(
                arguments["context_id"],
                arguments["task_id"],
                arguments["messages"],
                arguments.get("metadata"),
            )
            return result.model_dump()
        
        elif name == "save_tool_execution_feedback_memory":
            context_id = arguments["context_id"]
            plan_id = arguments["plan_id"]
            feedback = arguments["execution_feedback"]
            
            results = []
            for f in feedback:
                results.append(PlanExecutionResult(
                    plan_id=plan_id,
                    context_id=context_id,
                    step_id=f["step_id"],
                    tool_name=f.get("tool_name", ""),
                    domain=f.get("domain", ""),
                    success=f["success"],
                    input=f.get("input"),
                    output=f.get("output"),
                    error=f.get("error"),
                    execution_time=f.get("execution_time", 0.0),
                ))
            
            # 先从执行结果中学习
            for result in results:
                if result.tool_name:
                    # 调用learn_from_execution方法记录工具执行结果
                    await self.plan_adjuster.learn_from_execution(
                        context_id=context_id,
                        tool_name=result.tool_name,
                        success=result.success,
                        input_data=result.input,
                        output_data=result.output,
                    )
            
            # 然后调整计划
            context_plans = self._get_context_plans(context_id)
            if plan_id in context_plans:
                plan = context_plans[plan_id]
                adjusted = await self.plan_adjuster.adjust_plan(context_id, plan, results)
                updated_plan = Plan(
                    plan_id=plan.plan_id,
                    context_id=context_id,
                    query=plan.query,
                    steps=adjusted.adjusted_steps,
                    context=plan.context,
                    created_at=plan.created_at,
                )
                context_plans[plan_id] = updated_plan
                return {
                    "original_plan_id": adjusted.original_plan_id,
                    "context_id": adjusted.context_id,
                    "adjustment_reason": adjusted.adjustment_reason,
                    "skipped_steps": adjusted.skipped_steps,
                    "added_steps": [s.model_dump() for s in adjusted.added_steps],
                    "adjusted_steps": [s.model_dump() for s in adjusted.adjusted_steps],
                }
            return {"error": "Plan not found"}
        
        elif name == "compress_working_memory":
            result = await self.memory_manager.write_working_memory(
                arguments["context_id"],
                arguments["messages"],
                keep_recent_count=arguments.get("keep_recent_count", 2),
                metadata=arguments.get("metadata"),
            )
            return result
            
        elif name == "plan_tool_calls":
            context_id = arguments["context_id"]
            plan = await self.tool_planner.plan(context_id, arguments["query"])
            self._get_context_plans(context_id)[plan.plan_id] = plan
            return {
                "plan_id": plan.plan_id,
                "context_id": plan.context_id,
                "query": plan.query,
                "steps": [s.model_dump() for s in plan.steps],
                "context": plan.context,
                "created_at": plan.created_at,
            }

        elif name == "get_combined_memory":
            combined = await self.memory_manager.get_combined_memory(
                arguments["context_id"],
                arguments["query"],
                arguments.get("summarize", False),
            )
            return {"context_id": arguments["context_id"], "query": arguments["query"], **combined}
        return {"error": f"Unknown tool: {name}"}
