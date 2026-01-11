"""DynamicAdjuster - 基于执行结果动态调整工具调用规划，支持Context隔离"""

import json
from typing import List, Dict, Any, Optional

from ..memory import MemoryManager
from ..types import (
    Plan,
    PlanStep,
    PlanExecutionResult,
    AdjustedPlan,
    ToolDefinition,
)


class DynamicPlanAdjuster:
    """动态规划调整器 - 基于工具执行结果调整后续规划，支持Context隔离"""

    def __init__(self, memory_manager: MemoryManager, tool_registry = None):
        self.memory_manager = memory_manager
        self.tool_registry = tool_registry

    async def get_context_tools(self, context_id: str) -> List[ToolDefinition]:
        """获取当前Context注册的所有工具

        Args:
            context_id: Context ID

        Returns:
            工具定义列表
        """
        if self.tool_registry:
            return self.tool_registry.list_tools(context_id)
        return []

    async def summarize_all_tool_memory(self, context_id: str) -> str:
        """总结当前Context所有工具的使用记忆

        Args:
            context_id: Context ID

        Returns:
            工具使用总结
        """
        tools = await self.get_context_tools(context_id)
        if not tools:
            return "No tools registered for this context"

        tool_names = [tool.tool_name for tool in tools]
        app = await self.memory_manager._get_app()
        workspace_id = self.memory_manager._get_workspace_id(context_id)
        result = await app.async_execute(
            name="summary_tool_memory",
            workspace_id=workspace_id,
            tool_names=",".join(tool_names),
        )
        if result:
            memory_list = result.get("metadata", {}).get("memory_list", [])
            if memory_list:
                return memory_list[0].get("content", "")
        return "No tool memory available"

    async def analyze_execution_results(
        self, plan: Plan, results: List[PlanExecutionResult]
    ) -> Dict[str, Any]:
        """分析执行结果，确定是否需要调整

        Args:
            plan: 原始计划
            results: 执行结果列表

        Returns:
            分析结果
        """
        success_count = sum(1 for r in results if r.success)
        fail_count = len(results) - success_count

        failed_steps = [r for r in results if not r.success]
        successful_results = [r for r in results if r.success]

        analysis = {
            "total_steps": len(results),
            "success_count": success_count,
            "fail_count": fail_count,
            "failed_steps": [
                {
                    "step_id": r.step_id,
                    "error": r.error,
                }
                for r in failed_steps
            ],
            "needs_adjustment": fail_count > 0,
            "completion_rate": success_count / len(results) if results else 0.0,
        }

        return analysis

    async def _build_adjustment_prompt(
        self,
        context_id: str,
        plan: Plan,
        results: List[PlanExecutionResult],
        analysis: Dict[str, Any],
    ) -> str:
        """构建调整提示词

        Args:
            context_id: Context ID
            plan: 原始计划
            results: 执行结果
            analysis: 分析结果

        Returns:
            调整提示词
        """
        tool_memory_info = await self.summarize_all_tool_memory(context_id)

        results_summary = []
        for r in results:
            status = "成功" if r.success else "失败"
            results_summary.append(
                f"- Step {r.step_id}: {status}\n"
                f"  输出: {str(r.output)[:200] if r.output else 'None'}"
            )

        prompt = f"""你是一个智能规划调整助手，需要根据工具执行结果调整后续规划。

## Context信息
当前Context ID: {context_id}

## 原始计划
查询: {plan.query}
步骤数: {len(plan.steps)}

## 执行结果
{chr(10).join(results_summary)}

## 执行分析
- 总步骤数: {analysis['total_steps']}
- 成功: {analysis['success_count']}
- 失败: {analysis['fail_count']}
- 完成率: {analysis['completion_rate']:.1%}

## 工具使用经验
{tool_memory_info}

## 调整要求
1. 分析失败原因
2. 如果步骤失败，考虑是否需要重试、跳过或添加新步骤
3. 如果步骤成功但结果不理想，考虑是否需要调整后续参数
4. 输出调整后的计划或说明为什么不需要调整

请返回以下JSON格式的调整结果：
{{
    "needs_adjustment": true/false,
    "adjustment_reason": "调整原因说明",
    "skipped_steps": ["跳过的步骤ID"],
    "added_steps": [
        {{
            "step_id": "新步骤ID",
            "tool_name": "工具名",
            "domain": "工具领域",
            "parameters": {{参数字典}},
            "reasoning": "为什么添加这个步骤",
            "expected_output": "期望输出"
        }}
    ],
    "adjusted_steps": [
        {{
            "step_id": "步骤ID",
            "new_parameters": {{新的参数}},
            "reasoning": "调整原因"
        }}
    ]
}}

只返回JSON，不要有其他内容。如果不需要调整，设置 needs_adjustment 为 false。
"""
        return prompt

    async def adjust_plan(
        self, context_id: str, plan: Plan, results: List[PlanExecutionResult]
    ) -> AdjustedPlan:
        """根据执行结果调整计划（针对指定Context）

        Args:
            context_id: Context ID
            plan: 原始计划
            results: 执行结果列表

        Returns:
            调整后的计划
        """
        import json as json_lib

        analysis = await self.analyze_execution_results(plan, results)

        if not analysis["needs_adjustment"]:
            return AdjustedPlan(
                original_plan_id=plan.plan_id,
                context_id=context_id,
                adjusted_steps=plan.steps,
                adjustment_reason="No adjustment needed - all steps executed successfully",
                skipped_steps=[],
                added_steps=[],
            )

        prompt = await self._build_adjustment_prompt(context_id, plan, results, analysis)

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
                adjust_data = json_lib.loads(answer[json_start:json_end])
            else:
                raise ValueError("No JSON found in response")

            skipped_step_ids = set(adjust_data.get("skipped_steps", []))
            adjusted_steps = []
            for step in plan.steps:
                adjusted_info = next(
                    (a for a in adjust_data.get("adjusted_steps", [])
                     if a.get("step_id") == step.step_id),
                    None
                )
                if step.step_id in skipped_step_ids:
                    continue
                if adjusted_info:
                    step.parameters.update(adjusted_info.get("new_parameters", {}))
                adjusted_steps.append(step)

            added_steps = []
            for step_data in adjust_data.get("added_steps", []):
                added_step = PlanStep(
                    step_id=step_data.get("step_id", f"step_{len(adjusted_steps) + len(added_steps) + 1}"),
                    tool_name=step_data.get("tool_name", ""),
                    domain=step_data.get("domain", ""),
                    parameters=step_data.get("parameters", {}),
                    reasoning=step_data.get("reasoning", ""),
                    expected_output=step_data.get("expected_output", ""),
                )
                added_steps.append(added_step)
                adjusted_steps.append(added_step)

            adjusted_plan = AdjustedPlan(
                original_plan_id=plan.plan_id,
                context_id=context_id,
                adjusted_steps=adjusted_steps,
                adjustment_reason=adjust_data.get("adjustment_reason", "Adjusted based on execution results"),
                skipped_steps=list(skipped_step_ids),
                added_steps=added_steps,
            )

        except (json_lib.JSONDecodeError, ValueError) as e:
            adjusted_plan = AdjustedPlan(
                original_plan_id=plan.plan_id,
                context_id=context_id,
                adjusted_steps=plan.steps,
                adjustment_reason=f"Failed to parse adjustment: {str(e)}",
                skipped_steps=[],
                added_steps=[],
            )

        return adjusted_plan

    async def learn_from_execution(
        self, context_id: str, tool_name: str, success: bool,
        input_data: Dict, output_data: Any
    ) -> None:
        """从执行结果中学习（针对指定Context）

        Args:
            context_id: Context ID
            tool_name: 工具名
            success: 是否成功
            input_data: 输入数据
            output_data: 输出数据
        """
        await self.memory_manager.add_tool_call_result(
            context_id=context_id,
            tool_name=tool_name,
            tool_input=input_data,
            tool_output=output_data,
            execution_time=0.0,
        )
