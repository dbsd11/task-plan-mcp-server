"""Planner - 动态工具调用规划器，支持Context隔离"""

import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

from reme_ai import ReMeApp

from ..memory import MemoryManager
from ..types import (
    ToolDefinition,
    PlanStep,
    Plan,
)


class ToolPlanner:
    """动态工具调用规划器 - 支持Context隔离"""

    def __init__(self, memory_manager: MemoryManager, tool_registry = None):
        self.memory_manager = memory_manager
        self.tool_registry = tool_registry

    def get_available_tools(self, context_id: str = None) -> List[ToolDefinition]:
        """获取指定Context所有可用的工具

        Args:
            context_id: Context ID

        Returns:
            工具定义列表
        """
        if self.tool_registry:
            return self.tool_registry.list_tools(context_id)
        return []

    async def _build_planning_prompt(self, context_id: str, query: str,
                                     personal_memory: str,
                                     task_memory: str,
                                     tool_memory: str) -> str:
        """构建规划提示词

        Args:
            context_id: Context ID
            query: 用户查询
            personal_memory: 个人记忆
            task_memory: 任务记忆
            tool_memory: 工具记忆

        Returns:
            规划提示词
        """
        import json

        tools = self.get_available_tools(context_id)
        tools_info = []
        for tool in tools:
            tools_info.append(
                f"- Domain: {tool.domain}, Name: {tool.tool_name}\n"
                f"  Description: {tool.description}\n"
                f"  Args: {json.dumps(tool.args, ensure_ascii=False, indent=4)}"
            )

        tools_str = "\n".join(tools_info) if tools_info else "No tools registered"

        prompt = f"""你是一个智能规划助手，需要为用户查询规划工具调用步骤。

## Context信息
当前Context ID: {context_id}

## 可用工具
{tools_str}

## 用户查询
{query}

## 个人相关记忆
{personal_memory if personal_memory else "无"}

## 任务相关记忆
{task_memory if task_memory else "无"}

## 工具使用记忆
{tool_memory if tool_memory else "无"}

## 规划要求
1. 分析查询意图，确定需要调用的工具和顺序
2. 如果有依赖关系，确保前置步骤在依赖步骤之前
3. 输出JSON格式的规划结果
4. 每个步骤需要有清晰的执行理由

请返回以下JSON格式的规划结果：
{{
    "steps": [
        {{
            "step_id": "step_1",
            "tool_name": "工具名",
            "domain": "工具领域",
            "parameters": {{参数字典}},
            "depends_on": [],  // 依赖的步骤ID列表
            "reasoning": "为什么调用这个工具",
            "expected_output": "期望从这个工具获得什么"
        }}
    ],
    "context": {{
        "planning_notes": "规划备注"
    }}
}}

只返回JSON，不要有其他内容。
"""
        return prompt

    async def plan(self, context_id: str, query: str) -> Plan:
        """根据查询生成工具调用计划（针对指定Context）

        Args:
            context_id: Context ID
            query: 用户查询

        Returns:
            工具调用计划
        """
        import json

        personal_memory = await self.memory_manager.retrieve_personal_memory(context_id, query)
        task_memory = await self.memory_manager.retrieve_task_memory(context_id, query)
        # 检索工具使用记忆
        tool_memory = await self.memory_manager.retrieve_tool_memory(context_id, query)

        prompt = await self._build_planning_prompt(context_id, query, personal_memory, task_memory, tool_memory)

        app = await self.memory_manager._get_app()
        result = await app.async_execute(
            name="react",
            query=prompt,
        )

        answer = result.get("answer", "") if result else ""

        try:
            json_start = answer.find("{")
            json_end = answer.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                plan_data = json.loads(answer[json_start:json_end])
            else:
                raise ValueError("No JSON found in response")

            steps = []
            for step_data in plan_data.get("steps", []):
                step = PlanStep(
                    step_id=step_data.get("step_id", f"step_{len(steps) + 1}"),
                    tool_name=step_data.get("tool_name", ""),
                    domain=step_data.get("domain", ""),
                    parameters=step_data.get("parameters", {}),
                    depends_on=step_data.get("depends_on", []),
                    reasoning=step_data.get("reasoning", ""),
                    expected_output=step_data.get("expected_output", ""),
                )
                steps.append(step)

            plan = Plan(
                plan_id=f"plan_{uuid.uuid4().hex[:8]}",
                context_id=context_id,
                query=query,
                steps=steps,
                context=plan_data.get("context", {}),
                created_at=datetime.now().isoformat(),
            )

        except (json.JSONDecodeError, ValueError) as e:
            steps = []
            plan = Plan(
                plan_id=f"plan_{uuid.uuid4().hex[:8]}",
                context_id=context_id,
                query=query,
                steps=steps,
                context={"error": str(e), "raw_response": answer},
                created_at=datetime.now().isoformat(),
            )

        return plan

    def validate_tool_exists(self, tool_name: str, domain: str, context_id: str) -> bool:
        """验证工具是否存在

        Args:
            tool_name: 工具名
            domain: 工具领域
            context_id: Context ID

        Returns:
            是否存在
        """
        if self.tool_registry:
            return self.tool_registry.has_tool(tool_name, domain, context_id)
        return False

    def get_tool_definition(self, tool_name: str, domain: str, context_id: str) -> Optional[ToolDefinition]:
        """获取工具定义

        Args:
            tool_name: 工具名
            domain: 工具领域
            context_id: Context ID

        Returns:
            工具定义，如果不存在返回None
        """
        if self.tool_registry:
            return self.tool_registry.get(tool_name, domain, context_id)
        return None
