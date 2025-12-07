from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from .code_analyst_agent import create_code_analyst_agent
from .domain_context_agent import create_domain_context_agent
from .data_governance_agent import create_data_governance_agent
from .synthesizer_agent import create_synthesizer_agent
from dotenv import load_dotenv
import os

load_dotenv()


class DiscoveryState(TypedDict):
    pass


code_analyst_agent = create_code_analyst_agent(
    model_name=os.getenv("CODE_ANALYST_AGENT_MODEL_NAME")
)
domain_context_agent = create_domain_context_agent(
    model_name=os.getenv("DOMAIN_CONTEXT_AGENT_MODEL_NAME")
)
data_governance_agent = create_data_governance_agent(
    model_name=os.getenv("DATA_GOVERNANCE_AGENT_MODEL_NAME")
)
synthesizer_agent = create_synthesizer_agent(
    model_name=os.getenv("SYNTHESIZER_AGENT_MODEL_NAME")
)


def create_discovery_workflow():
    """Create and configure the discovery workflow"""

    workflow_builder = StateGraph(DiscoveryState)

    workflow_builder.add_node("code_analyst_agent", code_analyst_agent)
    workflow_builder.add_node("domain_context_agent", domain_context_agent)
    workflow_builder.add_node("data_governance_agent", data_governance_agent)
    workflow_builder.add_node("synthesizer_agent", synthesizer_agent)

    workflow_builder.add_edge(START, "code_analyst_agent")
    workflow_builder.add_edge(START, "domain_context_agent")
    workflow_builder.add_edge(START, "data_governance_agent")

    workflow_builder.add_edge("code_analyst_agent", "synthesizer_agent")
    workflow_builder.add_edge("domain_context_agent", "synthesizer_agent")
    workflow_builder.add_edge("data_governance_agent", "synthesizer_agent")

    workflow_builder.add_edge("synthesizer_agent", END)

    workflow = workflow_builder.compile()

    return workflow
