import operator
from typing import Annotated, Any, Dict, List, Literal, Optional, TypedDict
from langchain_core.messages import AnyMessage


class AgentContribution(TypedDict):
    agent: str
    action: str
    summary: str
    timestamp: Optional[str]
    metadata: Optional[Dict[str, Any]]


class AgentState(TypedDict):
    messages: Annotated[List[AnyMessage], operator.add]
    user_query: str
    current_task: Optional[str]
    research_data: Optional[str]
    analysis_data: Optional[str]
    agent_history: Annotated[List[AgentContribution], operator.add]
    next_agent: Literal["researcher", "analyst", "validator", "FINISH"]
    supervisor_reasoning: Optional[str]
    validation_passed: bool
    validation_feedback: Optional[str]
    final_synthesis: Optional[str]
    iteration_count: int
    max_iterations: int
