"""Memory模块 - 定义数据类型"""
import uuid
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


def generate_context_id() -> str:
    """生成唯一的context ID"""
    return f"ctx_{uuid.uuid4().hex[:12]}"


class ToolDefinition(BaseModel):
    """客户端工具定义"""
    domain: str = Field(..., description="工具领域")
    tool_name: str = Field(..., description="工具名称")
    description: str = Field(..., description="工具描述")
    args: Dict[str, Any] = Field(default_factory=dict, description="工具参数schema")
    output: Dict[str, Any] = Field(default_factory=dict, description="工具输出schema")


class PlanStep(BaseModel):
    """规划步骤"""
    step_id: str = Field(..., description="步骤ID")
    tool_name: str = Field(..., description="要调用的工具名")
    domain: str = Field(..., description="工具领域")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="调用参数")
    depends_on: List[str] = Field(default_factory=list, description="依赖的步骤ID")
    reasoning: str = Field(default="", description="执行此步骤的原因")
    expected_output: str = Field(default="", description="期望的输出")


class Plan(BaseModel):
    """Tool调用计划"""
    plan_id: str = Field(default_factory=lambda: f"plan_{uuid.uuid4().hex[:8]}", description="计划ID")
    context_id: str = Field(..., description="所属的Context ID")
    query: str = Field(..., description="用户查询")
    steps: List[PlanStep] = Field(default_factory=list, description="执行步骤列表")
    context: Dict[str, Any] = Field(default_factory=dict, description="计划上下文")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="创建时间")


class PlanExecutionResult(BaseModel):
    """计划执行结果"""
    plan_id: str = Field(default="", description="计划ID")
    context_id: str = Field(default="", description="Context ID")
    step_id: str = Field(..., description="步骤ID")
    tool_name: str = Field(default="", description="工具名称")
    domain: str = Field(default="", description="工具领域")
    success: bool = Field(..., description="是否成功")
    input: Any = Field(default=None, description="工具输入")
    output: Any = Field(default=None, description="工具输出")
    error: Optional[str] = Field(default=None, description="错误信息")
    create_time: str = Field(default="", description="创建时间 %Y-%m-%d %H:%M:%S")
    execution_time: float = Field(default=0.0, description="执行时间")


class AdjustedPlan(BaseModel):
    """调整后的计划"""
    original_plan_id: str = Field(..., description="原计划ID")
    context_id: str = Field(..., description="Context ID")
    adjusted_steps: List[PlanStep] = Field(..., description="调整后的步骤")
    adjustment_reason: str = Field(..., description="调整原因")
    skipped_steps: List[str] = Field(default_factory=list, description="跳过的步骤ID")
    added_steps: List[PlanStep] = Field(default_factory=list, description="新增的步骤ID")


class ContextConfig(BaseModel):
    """Context配置"""
    context_id: str = Field(default_factory=generate_context_id, description="Context唯一ID")
    name: str = Field(default="", description="Context名称")
    description: str = Field(default="", description="Context描述")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="创建时间")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


class ContextInfo(BaseModel):
    """Context信息"""
    context_id: str = Field(..., description="Context ID")
    name: str = Field(default="", description="Context名称")
    description: str = Field(default="", description="Context描述")
    memory_stats: Dict[str, Any] = Field(default_factory=dict, description="记忆统计")
    created_at: str = Field(default="", description="创建时间")
    last_accessed: str = Field(default="", description="最后访问时间")


class ExecutionFeedback(BaseModel):
    """执行反馈"""
    step_id: str = Field(..., description="步骤ID")
    tool_name: str = Field(default="", description="工具名称")
    domain: str = Field(default="", description="工具领域")
    success: bool = Field(..., description="是否成功")
    output: Any = Field(default=None, description="工具输出")
    error: Optional[str] = Field(default=None, description="错误信息")
    execution_time: float = Field(default=0.0, description="执行时间")


class PersonalMemoryContent(BaseModel):
    """Personal Memory内容"""
    messages: List[Dict[str, Any]] = Field(..., description="对话消息列表")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


class ToolCallResult(BaseModel):
    """工具调用结果"""
    tool_name: str = Field(..., description="工具名称")
    tool_input: Dict[str, Any] = Field(..., description="工具输入")
    tool_output: Any = Field(..., description="工具输出")
    execution_time: float = Field(default=0.0, description="执行时间")


class WorkingMemoryContext(BaseModel):
    """工作记忆上下文"""
    task_id: str = Field(..., description="任务ID")
    content: str = Field(..., description="工作记忆内容")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


class MemoryOperationResult(BaseModel):
    """记忆操作结果"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(default="", description="消息")
    memory_type: str = Field(default="", description="记忆类型")
    context_id: str = Field(default="", description="Context ID")


class EntityRelationship(BaseModel):
    """实体关系"""
    target_entity_id: str = Field(..., description="关联实体ID")
    relationship_type: str = Field(..., description="关系类型")
    description: str = Field(default="", description="关系描述")


class Entity(BaseModel):
    """实体定义"""
    entity_id: str = Field(..., description="实体唯一标识")
    entity_type: str = Field(..., description="实体类型")
    name: str = Field(..., description="实体名称")
    description: str = Field(default="", description="实体描述")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="实体属性")
    relationships: List[EntityRelationship] = Field(default_factory=list, description="实体关系")


class EntityMemoryContent(BaseModel):
    """Entity Memory内容"""
    entities: List[Entity] = Field(..., description="实体列表")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
