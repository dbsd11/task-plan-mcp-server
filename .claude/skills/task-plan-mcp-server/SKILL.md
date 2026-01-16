# task-plan-mcp-server

基于 Python + ReMe 内存集成的任务规划与动态工具规划 MCP Server，通过 SSE 协议提供上下文管理、规划反馈和动态规划能力。

## 核心设计

本 MCP Server 遵循**响应式内存管理**理念（类 React 思想）：

- **单一数据源**：上下文记忆是任务状态的唯一数据源
- **即时同步**：每次状态变更（决策、工具调用结果）立即同步到内存
- **兜底检查**：任务结束前必须检查内存一致性

## 工具列表

| 工具 | 用途 | 关键参数 |
|------|------|----------|
| `create_context` | 创建规划上下文 | `name`(必填), `parent_context_id` |
| `plan_tool_calls` | 动态规划工具调用序列 | `context_id`, `query` |
| `report_context_memory` | 上报上下文记忆 | `context_id`, `type`, `messages`/`tool_execution_feedback` |

## 使用场景

1. **任务规划**：需要动态规划工具调用序列时
2. **上下文管理**：需要隔离和复用任务记忆时
3. **经验沉淀**：需要记录和查询历史执行经验时

## 工作流

本 Skill 提供两个核心工作流：

### 1. Server 部署检查 (setup-checklist.yaml)

确保 MCP Server 正确部署和配置，包括：
- 环境依赖检查
- 配置文件验证
- 连接测试

### 2. 运行时最佳实践 (runtime-checklist.yaml)

确保遵循响应式内存管理最佳实践，包括：
- 上下文创建时机
- 反馈记录完整性
- 兜底检查机制

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 启动 MCP Server
python -m src.main
```

## 关键建议

1. **先创建上下文**：任何操作前必须先调用 `create_context`
2. **立即同步反馈**：工具调用后立即记录反馈，不要延迟
3. **复用上下文**：相似任务通过 `parent_context_id` 复用历史
4. **兜底检查**：任务结束前必须检查内存一致性

## 相关文件

- [项目源码](src/)
- [工具定义](src/tool_call.py)
- [内存管理](src/memory/)
- [集成配置](integration/)