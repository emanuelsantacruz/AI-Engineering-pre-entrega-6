from typing import Literal
from langgraph.graph import StateGraph, START, END

from state import AgentState
from agents.supervisor import supervisor_node, validator_node
from agents.research_agent import research_node
from agents.analyst_agent import analyst_node


def route_supervisor(state: AgentState) -> Literal["researcher", "analyst", "validator", "__end__"]:
    decision = state.get("next_agent")
    if decision == "researcher":
        return "researcher"
    elif decision == "analyst":
        return "analyst"
    elif decision == "validator":
        return "validator"
    elif decision == "FINISH":
        return END
    return END


def route_validator(state: AgentState) -> Literal["supervisor", "__end__"]:
    if state.get("validation_passed", False):
        return END
    return "supervisor"


def build_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("researcher", research_node)
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("validator", validator_node)

    workflow.add_edge(START, "supervisor")

    workflow.add_conditional_edges(
        "supervisor",
        route_supervisor,
        {
            "researcher": "researcher",
            "analyst": "analyst",
            "validator": "validator",
            END: END
        }
    )

    workflow.add_edge("researcher", "supervisor")
    workflow.add_edge("analyst", "supervisor")

    workflow.add_conditional_edges(
        "validator",
        route_validator,
        {
            END: END,
            "supervisor": "supervisor"
        }
    )

    return workflow.compile()


def export_graph_mermaid(app) -> str:
    return app.get_graph().draw_mermaid()
