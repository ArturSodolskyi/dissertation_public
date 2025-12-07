from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv

from agents.development.task_iterator_agent import create_task_iterator_agent
from agents.discovery.workflow import create_discovery_workflow
from agents.planning.tasks_planner_agent import create_tasks_planner_agent
import os

load_dotenv()


class State(TypedDict):
    pass


def create_workflow():
    discovery_workflow = create_discovery_workflow()
    planning_agent = create_tasks_planner_agent(
        model_name=os.getenv("TASK_PLANNER_AGENT_MODEL_NAME")
    )
    development_agent = create_task_iterator_agent(
        model_name=os.getenv("TASK_ITERATOR_AGENT_MODEL_NAME")
    )

    workflow = StateGraph(State)

    workflow.add_node("discovery", discovery_workflow)
    workflow.add_node("planning", planning_agent)
    workflow.add_node("development", development_agent)

    workflow.add_edge(START, "discovery")
    workflow.add_edge("discovery", "planning")
    workflow.add_edge("planning", "development")
    workflow.add_edge("development", END)

    return workflow.compile()


def main():

    agent = create_workflow()

    query = "Let's start the workflow"

    for chunk in agent.stream(
        {"messages": [{"role": "user", "content": query}]},
        stream_mode="values",
    ):
        if "messages" in chunk:
            chunk["messages"][-1].pretty_print()


if __name__ == "__main__":
    main()
