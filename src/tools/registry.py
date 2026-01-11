"""ToolRegistry - 客户端工具注册表"""

from typing import Dict, Optional
from ..types import ToolDefinition


class ToolRegistry:
    """工具注册表 - 管理客户端注册的tool"""

    def __init__(self):
        self._tools: Dict[str, Dict[str, ToolDefinition]] = {}

    def register(self, tool: ToolDefinition, context_id: str) -> bool:
        """注册工具

        Args:
            tool: 工具定义
            context_id: Context ID

        Returns:
            是否成功
        """
        if context_id not in self._tools:
            self._tools[context_id] = {}
        key = f"{tool.domain}.{tool.tool_name}"
        self._tools[context_id][key] = tool
        return True

    def register_batch(self, tools: list, context_id: str) -> int:
        """批量注册工具

        Args:
            tools: 工具定义列表
            context_id: Context ID

        Returns:
            成功注册的工具数量
        """
        if context_id not in self._tools:
            self._tools[context_id] = {}
        count = 0
        for tool in tools:
            if self.register(tool, context_id):
                count += 1
        return count

    def get(self, tool_name: str, domain: str, context_id: str) -> Optional[ToolDefinition]:
        """获取工具定义

        Args:
            tool_name: 工具名
            domain: 工具领域
            context_id: Context ID

        Returns:
            工具定义，不存在返回None
        """
        if context_id not in self._tools:
            return None
        key = f"{domain}.{tool_name}"
        return self._tools[context_id].get(key)

    def list_tools(self, context_id: str) -> list:
        """列出指定Context的所有工具

        Args:
            context_id: Context ID

        Returns:
            工具定义列表
        """
        if context_id not in self._tools:
            return []
        return list(self._tools[context_id].values())

    def list_all_tools(self) -> list:
        """列出所有Context的所有工具"""
        all_tools = []
        for context_tools in self._tools.values():
            all_tools.extend(context_tools.values())
        return all_tools

    def has_tool(self, tool_name: str, domain: str, context_id: str) -> bool:
        """检查工具是否存在"""
        if context_id not in self._tools:
            return False
        key = f"{domain}.{tool_name}"
        return key in self._tools[context_id]

    def remove(self, tool_name: str, domain: str, context_id: str) -> bool:
        """移除工具

        Args:
            tool_name: 工具名
            domain: 工具领域
            context_id: Context ID

        Returns:
            是否成功
        """
        if context_id not in self._tools:
            return False
        key = f"{domain}.{tool_name}"
        if key in self._tools[context_id]:
            del self._tools[context_id][key]
            return True
        return False

    def clear_context(self, context_id: str):
        """清空指定Context的所有工具

        Args:
            context_id: Context ID
        """
        if context_id in self._tools:
            self._tools[context_id].clear()

    def clear(self):
        """清空所有工具"""
        self._tools.clear()

    def count(self, context_id: str = None) -> int:
        """获取工具数量

        Args:
            context_id: Context ID，为None时返回总数

        Returns:
            工具数量
        """
        if context_id is None:
            total = 0
            for context_tools in self._tools.values():
                total += len(context_tools)
            return total
        return len(self._tools.get(context_id, {}))
