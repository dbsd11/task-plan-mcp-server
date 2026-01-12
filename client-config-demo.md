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
# 参考信息
任务规划mcp：task plan server

# 任务
查看项目结构

# 输出及要求
使用任务规划mcp的tool对任务执行过程中的上下文进行管理(创建上下文/plan反馈保存/tool执行结果保存)
```