from langchain_core.messages import AIMessage
from langgraph.graph import MessagesState
from langgraph.graph import END, StateGraph, START

from agents.development.code_quality_agent import create_code_quality_agent
from agents.development.implementation_agent import create_implementation_agent
from dotenv import load_dotenv
import os

load_dotenv()


class DevelopmentState(MessagesState):
    error: str | None
    iterations: int


MAX_ITERATIONS = 25

implementation_agent = create_implementation_agent(
    model_name=os.getenv("IMPLEMENTATION_AGENT_MODEL_NAME")
)
code_quality_agent = create_code_quality_agent(
    model_name=os.getenv("CODE_QUALITY_AGENT_MODEL_NAME")
)


def check(state: DevelopmentState) -> DevelopmentState:
    quality_report = code_quality_agent.invoke({"messages": state["messages"]})
    report_data = quality_report.get("structured_output", {})
    has_critical_issues = report_data.get("has_critical_issues", False)
    errors = report_data.get("errors", [])

    if has_critical_issues:
        error_message = f"Critical code quality issues found:\n"
        for error in errors:
            error_message += f"- {error}\n"

        return {
            **state,
            "error": f"Code Quality Check Failed:\n{error_message}",
        }

    return {
        **state,
        "error": None,
        "messages": state["messages"]
        + [AIMessage(content=f"Code Quality Check Passed")],
    }


def reflect(state: DevelopmentState):
    reflection = f"""
    Reflection: 
    Errors detected during code quality check: {state['error']}

    Analyze the errors and fix the code accordingly.
    """
    return {
        **state,
        "messages": state["messages"]
        + [
            AIMessage(reflection),
        ],
        "iterations": state["iterations"] + 1,
    }


def is_reflection_needed(state: DevelopmentState):
    state
    if state["error"] is None:
        return "next"

    if state["iterations"] == MAX_ITERATIONS:
        return "end"

    return "reflect"


def create_development_workflow():
    workflow = StateGraph(DevelopmentState)

    workflow.add_node("generate", implementation_agent)
    workflow.add_node("check", check)
    workflow.add_node("reflect", reflect)

    workflow.add_edge(START, "generate")
    workflow.add_edge("generate", "check")
    workflow.add_conditional_edges(
        "check",
        is_reflection_needed,
        {"end": END, "reflect": "reflect", "next": END},
    )
    workflow.add_edge("reflect", "generate")
    workflow.add_edge("reflect", END)
    return workflow.compile()
