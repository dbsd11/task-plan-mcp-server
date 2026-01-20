---
name: Task Plan Assistant
description: 智能任务规划与执行助手，帮助您完成复杂任务的分解、规划和执行追踪
---

# Task Plan Assistant

智能任务规划与执行助手，提供复杂任务分解、工具调用规划、执行进度追踪和经验沉淀功能。

## 核心能力

Task Plan Assistant 基于 `task-plan-mcp-server` 运行，提供三个核心工具支持您的任务管理：

### 1. 上下文管理 (create_context)
每个任务从创建独立的规划上下文开始，确保任务记忆隔离和经验可追溯。

详细信息请参考：[create-context.yml](workflows/create-context.yml)

### 2. 智能规划 (decision)
根据任务动态生成执行计划，将复杂任务分解为可执行的步骤序列。

详细信息请参考：[decision.yml](workflows/decision.yml)

### 3. 执行追踪 (report_action_result)
统一上报执行结果和决策反馈，支持实时追踪和经验复用。

详细信息请参考：[report-action-result.yml](workflows/report-action-result.yml)

## 任务执行标准流程

### 第一阶段：任务开始

1. 调用 `create_context` 创建上下文
2. 记录返回的 `context_id`
3. 配置任务描述和代理信息
4. 检查是否存在可复用的父上下文

### 第二阶段：任务执行

1. 调用 `decision` 获取执行计划
2. 按顺序执行计划中的每个步骤
3. 每个工具调用后立即上报执行结果
4. 遇到重要决策时记录计划反馈
5. **最后一步必须执行 report_action_result**：确保所有执行结果同步到内存

### 第三阶段：任务收尾

1. 确认所有执行步骤已完成
2. 确认所有执行结果已上报
3. 如有遗漏，立即补报

## 快速开始

```json
{
  "name": "my_task",
  "description": "任务描述",
  "agent": {
    "name": "Claude",
    "role": "assistant"
  }
}
```

调用 `create_context` 获取 context_id，然后使用 `decision` 进行规划，最后通过 `report_action_result` 追踪执行结果。

## 工具集成

本 Skill 深度集成以下 MCP 工具：

- **create_context**：创建和管理规划上下文
- **decision**：智能任务规划和步骤生成
- **report_action_result**：执行结果上报和反馈收集

所有工具协同工作，形成完整的任务管理和执行追踪闭环。
