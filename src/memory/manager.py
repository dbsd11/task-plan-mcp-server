"""Memory管理器 - 封装ReMe的memory操作，支持Context隔离"""

import json
from typing import List, Dict, Any, Optional

from reme_ai import ReMeApp

from ..types import (
    ContextConfig,
    ContextInfo,
    MemoryOperationResult,
    generate_context_id,
)


class MemoryManager:
    """Memory管理器 - 支持Context隔离的memory操作"""

    def __init__(self, llm_model: str, embedding_model: str, vector_store_backend: str = "memory", tool_registry = None):
        self.llm_model = llm_model
        self.embedding_model = embedding_model
        self.vector_store_backend = vector_store_backend
        self._base_workspace_id = "reme_mcp_workspace"
        self._contexts: Dict[str, ContextConfig] = {}
        self._tool_registry = tool_registry

        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_file_path = os.path.join(current_dir, "config.yaml")
        self._app = ReMeApp(
            f"llm.default.model_name={self.llm_model}",
            f"embedding_model.default.model_name={self.embedding_model}",
            f"vector_store.default.backend={self.vector_store_backend}",
            config_path=config_file_path
        )
        self._app.start()

    async def _get_app(self) -> ReMeApp:
        """获取ReMeApp实例"""
        return self._app

    def _get_workspace_id(self, context_id: str) -> str:
        """根据context_id生成workspace_id"""
        return f"{self._base_workspace_id}_{context_id}"

    async def close(self):
        """关闭App实例"""
        if self._app:
            await self._app.stop()
            self._app = None

    def create_context(self, name: str = "", description: str = "", agent_info: Optional[Dict[str, Any]] = None,
                       metadata: Optional[Dict[str, Any]] = None,
                       parent_context_id: Optional[str] = None) -> ContextConfig:
        """创建新的Context

        Args:
            name: Context名称
            description: Context描述
            agent_info: 智能体信息（可选）
            metadata: 元数据
            parent_context_id: 父Context ID（可选），用于创建层级关系

        Returns:
            Context配置
        """
        context_id = generate_context_id()
        config = ContextConfig(
            context_id=context_id,
            name=name,
            description=description,
            agent_info=agent_info,
            metadata=metadata or {},
            parent_context_id=parent_context_id,
        )
        self._contexts[context_id] = config
        return config

    def get_context(self, context_id: str) -> Optional[ContextConfig]:
        """获取Context配置

        Args:
            context_id: Context ID

        Returns:
            Context配置，不存在返回None
        """
        return self._contexts.get(context_id)

    def list_contexts(self) -> List[ContextInfo]:
        """列出所有Context

        Returns:
            Context信息列表
        """
        infos = []
        for config in self._contexts.values():
            infos.append(ContextInfo(
                context_id=config.context_id,
                name=config.name,
                description=config.description,
                created_at=config.created_at,
            ))
        return infos

    def delete_context(self, context_id: str) -> bool:
        """删除Context

        Args:
            context_id: Context ID

        Returns:
            是否成功
        """
        if context_id in self._contexts:
            del self._contexts[context_id]
            return True
        return False

    async def clear_context(self, context_id: str) -> bool:
        """清空指定Context的所有记忆

        Args:
            context_id: Context ID

        Returns:
            是否成功
        """
        app = await self._get_app()
        workspace_id = self._get_workspace_id(context_id)
        await app.async_execute(
            name="vector_store",
            workspace_id=workspace_id,
            action="delete",
        )
        return True

    async def set_personal_memory(self, context_id: str, messages: List[Dict[str, Any]],
                                   metadata: Optional[Dict[str, Any]] = None) -> MemoryOperationResult:
        """预设Personal Memory

        Args:
            context_id: Context ID
            messages: 对话消息列表 [{"role": "user|assistant", "content": "..."}]
            metadata: 元数据

        Returns:
            操作结果
        """
        app = await self._get_app()
        workspace_id = self._get_workspace_id(context_id)
        result = await app.async_execute(
            name="summary_personal_memory",
            trajectories=[
                {"messages": messages, "score": 1.0},
            ],
            workspace_id=workspace_id,
            extra_info=metadata or {},
        )
        return MemoryOperationResult(
            success=result.get("success", False),
            message="Personal memory set",
            memory_type="personal",
            context_id=context_id,
        )

    async def save_plan_feedback_memory(self, context_id: str, plan_id: str,
                              messages: List[Dict[str, Any]],
                              metadata: Optional[Dict[str, Any]] = None) -> MemoryOperationResult:
        """Save Plan Memory

        Args:
            context_id: Context ID
            plan_id: 计划ID
            messages: 对话消息列表 [{"role": "user|assistant", "content": "..."}]
            metadata: 元数据

        Returns:
            操作结果
        """
        app = await self._get_app()
        workspace_id = self._get_workspace_id(context_id)
        result = await app.async_execute(
            name="summary_task_memory",
            trajectories=[
                {"messages": messages, "score": 1.0},
            ],
            workspace_id=workspace_id,
            extra_info={
                **(metadata or {}),
                "plan_id": plan_id,
            },
        )
        return MemoryOperationResult(
            success=result is not None,
            message="Task memory set",
            memory_type="task",
            context_id=context_id,
        )

    async def retrieve_personal_memory(self, context_id: str, query: str) -> str:
        """检索Personal Memory

        Args:
            context_id: Context ID
            query: 查询语句

        Returns:
            检索到的记忆内容
        """
        app = await self._get_app()
        workspace_id = self._get_workspace_id(context_id)
        result = await app.async_execute(
            name="retrieve_personal_memory",
            query=query,
            workspace_id=workspace_id,
        )
        return result.get("answer", "") if result else ""

    async def retrieve_task_memory(self, context_id: str, query: str) -> str:
        """检索Task Memory

        Args:
            context_id: Context ID
            query: 查询语句

        Returns:
            检索到的记忆内容
        """
        app = await self._get_app()
        workspace_id = self._get_workspace_id(context_id)
        result = await app.async_execute(
            name="retrieve_task_memory",
            workspace_id=workspace_id,
            query=query,
        )
        return result.get("answer", "") if result else ""

    async def add_tool_call_result(self, context_id: str, tool_name: str,
                                    tool_input: Dict[str, Any], tool_output: Any,
                                    success: bool, create_time: str,
                                    execution_time: float = 0.0,
                                    token_cost: int = 0) -> MemoryOperationResult:
        """添加工具调用结果到Tool Memory

        Args:
            context_id: Context ID
            tool_name: 工具名称
            tool_input: 工具输入
            tool_output: 工具输出
            execution_time: 执行时间

        Returns:
            操作结果
        """
        app = await self._get_app()
        workspace_id = self._get_workspace_id(context_id)
        result = await app.async_execute(
            name="add_tool_call_result",
            workspace_id=workspace_id,
            tool_call_results=[
                {
                    "tool_name": tool_name,
                    "input": json.dumps(tool_input, ensure_ascii=False),
                    "output": json.dumps(tool_output, ensure_ascii=False),
                    "success": success,
                    "create_time": create_time,
                    "time_cost": execution_time,
                    "token_cost": token_cost,
                }
            ],
        )
        return MemoryOperationResult(
            success=result["success"],
            message=json.dumps(result["metadata"], ensure_ascii=False),
            memory_type="tool",
            context_id=context_id,
        )

    async def retrieve_tool_memory(self, context_id: str, tool_name: str) -> str:
        """检索Tool Memory

        Args:
            context_id: Context ID
            tool_name: 工具名称

        Returns:
            检索到的工具使用记忆
        """
        app = await self._get_app()
        workspace_id = self._get_workspace_id(context_id)
        result = await app.async_execute(
            name="retrieve_tool_memory",
            workspace_id=workspace_id,
            tool_names=tool_name,
        )
        if result:
            memory_list = result.get("metadata", {}).get("memory_list", [])
            if memory_list:
                return "\n".join(m.get("content", "") for m in memory_list)
        return ""

    async def summarize_tool_memory(self, context_id: str, tool_name: str) -> str:
        """总结工具使用模式

        Args:
            context_id: Context ID
            tool_name: 工具名称

        Returns:
            工具使用总结
        """
        app = await self._get_app()
        workspace_id = self._get_workspace_id(context_id)
        result = await app.async_execute(
            name="summary_tool_memory",
            workspace_id=workspace_id,
            tool_names=tool_name,
        )
        if result:
            memory_list = result.get("metadata", {}).get("memory_list", [])
            if memory_list:
                return memory_list[0].get("content", "")
        return ""

    async def summarize_all_tool_memory(self, context_id: str) -> str:
        """总结当前Context所有工具的使用记忆

        Args:
            context_id: Context ID

        Returns:
            工具使用总结
        """
        if not self._tool_registry:
            return "No tool registry available"
            
        registered_tools = self._tool_registry.list_tools(context_id)
        if not registered_tools:
            return "No tools registered for this context"

        tool_names = ",".join([tool.tool_name for tool in registered_tools])
        return await self.summarize_tool_memory(context_id, tool_names)

    async def write_working_memory(self, context_id: str, messages: List[Dict[str, Any]],
                                    working_summary_mode: str = "auto",
                                    compact_ratio_threshold: float = 0.75,
                                    max_total_tokens: int = 20000,
                                    max_tool_message_tokens: int = 2000,
                                    keep_recent_count: int = 2,
                                    metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """写入Working Memory并获取压缩后的上下文

        Args:
            context_id: Context ID
            task_id: 任务ID
            messages: 待压缩的消息列表
            working_summary_mode: 压缩模式 (auto/manual)
            compact_ratio_threshold: 压缩比率阈值
            max_total_tokens: 最大总token数
            max_tool_message_tokens: 工具消息最大token数
            keep_recent_count: 保留的最近消息数量
            store_dir: 工作记忆存储目录
            metadata: 元数据

        Returns:
            压缩后的消息列表及其他结果信息
        """
        app = await self._get_app()
        workspace_id = self._get_workspace_id(context_id)

        result = await app.async_execute(
            name="summary_working_memory",
            messages=messages,
            working_summary_mode=working_summary_mode,
            compact_ratio_threshold=compact_ratio_threshold,
            max_total_tokens=max_total_tokens,
            max_tool_message_tokens=max_tool_message_tokens,
            group_token_threshold=None,
            keep_recent_count=keep_recent_count,
            workspace_id=workspace_id,
            extra_info={
                **(metadata or {}),
            },
        )

        return {
            "success": result is not None,
            "message": "Working memory processed",
            "compressed_messages": result.get("answer", []) if result else messages,
            "context_id": context_id,
            "metadata": result.get("metadata", {}) if result else {},
        }

    async def read_working_memory(self, context_id: str, task_id: str) -> str:
        """读取Working Memory

        Args:
            context_id: Context ID
            task_id: 任务ID

        Returns:
            工作记忆内容
        """
        return await self.retrieve_task_memory(context_id, f"Task: {task_id}")

    async def clear_working_memory(self, context_id: str, task_id: str) -> MemoryOperationResult:
        """清除特定任务的Working Memory

        Args:
            context_id: Context ID
            task_id: 任务ID

        Returns:
            操作结果
        """
        app = await self._get_app()
        workspace_id = self._get_workspace_id(context_id)
        messages = [{"role": "user", "content": f"Clear task {task_id} memory"}]
        result = await app.async_execute(
            name="summary_task_memory",
            workspace_id=workspace_id,
            trajectories=[
                {"messages": messages, "score": 0.0},
            ],
        )
        return MemoryOperationResult(
            success=result is not None,
            message="Working memory cleared",
            memory_type="working",
            context_id=context_id,
        )

    async def dump_memory(self, context_id: str, path: str) -> MemoryOperationResult:
        """导出指定Context的Memory到磁盘

        Args:
            context_id: Context ID
            path: 目标路径

        Returns:
            操作结果
        """
        app = await self._get_app()
        workspace_id = self._get_workspace_id(context_id)
        result = await app.async_execute(
            name="vector_store",
            workspace_id=workspace_id,
            action="dump",
            path=path,
        )
        return MemoryOperationResult(
            success=result is not None,
            message=f"Memory dumped to {path}",
            memory_type="all",
            context_id=context_id,
        )

    async def load_memory(self, context_id: str, path: str) -> MemoryOperationResult:
        """从磁盘加载Memory到指定Context

        Args:
            context_id: Context ID
            path: 源路径

        Returns:
            操作结果
        """
        app = await self._get_app()
        workspace_id = self._get_workspace_id(context_id)
        result = await app.async_execute(
            name="vector_store",
            workspace_id=workspace_id,
            action="load",
            path=path,
        )
        return MemoryOperationResult(
            success=result is not None,
            message=f"Memory loaded from {path}",
            memory_type="all",
            context_id=context_id,
        )

    async def get_combined_memory(self, context_id: str, query: str, summarize: bool = False,
                                   include_parent: bool = False, max_depth: int = 2) -> Dict[str, str]:
        """获取组合的memory（personal + task + tool）

        Args:
            context_id: Context ID
            query: 查询语句
            summarize: 是否总结工具记忆
            include_parent: 是否包含父Context的memory
            max_depth: 最大递归深度

        Returns:
            组合的记忆内容
        """
        personal = await self.retrieve_personal_memory(context_id, query)
        task = await self.retrieve_task_memory(context_id, query)

        # 基于tool registry获取context注册的所有工具名
        tool_names = ""
        if self._tool_registry:
            registered_tools = self._tool_registry.list_tools(context_id)
            if registered_tools:
                tool_names = ",".join([tool.tool_name for tool in registered_tools])

        if summarize:
            tool_memory = await self.summarize_tool_memory(context_id, tool_names)
        else:
            tool_memory = await self.retrieve_tool_memory(context_id, tool_names)

        result = {
            "personal_memory": personal,
            "task_memory": task,
            "tool_memory": tool_memory,
        }

        if include_parent and max_depth > 0:
            config = self.get_context(context_id)
            if config and config.parent_context_id:
                parent_memory = await self.get_combined_memory(
                    context_id=config.parent_context_id,
                    query=query,
                    summarize=summarize,
                    include_parent=True,
                    max_depth=max_depth - 1
                )
                result["parent_memory"] = parent_memory

        return result
