# mcp client 配置示例
{
  "mcpServers": {
    "task-plan-mcp-server": {
      "url": "http://localhost:58080/sse",
      "transport": "sse"
    }
  }
}

# 提示词示例
```markdown
请使用任务规划mcp（尽量采集agent执行信息并复用类似任务的上下文）：xxxx
```