
from typing import List, Dict
from enum import Enum
from pydantic import BaseModel, Field
from langchain_core.messages import (
    AnyMessage,
)

from langgraph.graph import (
    START,
    StateGraph,
    END,
)
from langgraph.graph.message import add_messages

from pydantic import BaseModel
from typing import Annotated, List
from langchain_core.messages.utils import AnyMessage
from langgraph.graph.message import add_messages


from typing import Optional
from .agents.supervisor import supervisor_node
from .agents.gad_7_scorer import GAD7AgentOutput, gad_7_scorer_node
from .agents.phq_9_scorer import PHQ9AgentOutput, phq_9_scorer_node
from .types import Route, MetricEnum

# class Route(str, Enum):
#     depression = "depression"
#     anxiety = "anxiety"
#     neither = "end"


class AppState(BaseModel):
    messages: Annotated[List[AnyMessage], add_messages]
    all_therapy_sessions: List[Dict] = Field(default_factory=list)
    diagnosis: str = ""
    metric: Optional[MetricEnum] = None
    gad_7_output: Optional[GAD7AgentOutput] = None
    route: Optional[Route] = None
    phq_9_output: Optional[PHQ9AgentOutput] = None
    output: Optional[GAD7AgentOutput | PHQ9AgentOutput] = None


def route_decision(state):
    print(f"Current route: {state.route}")
    if state.route == Route.depression:
        print("Routing to PHQ-9 Scorer")
        return Route.depression
    elif state.route == Route.anxiety:
        print("Routing to GAD-7 Scorer")
        return Route.anxiety
    else:
        return "end"


def build_graph():

    graph = StateGraph(AppState)

    graph.add_node("supervisor", supervisor_node)
    graph.add_node("gad_7_scorer", gad_7_scorer_node)
    graph.add_node("phq_9_scorer", phq_9_scorer_node)

    graph.add_edge(START, "supervisor")
    graph.add_conditional_edges(
        "supervisor",
        route_decision,
        {
            Route.anxiety.value: "gad_7_scorer",
            Route.depression.value: "phq_9_scorer",
            "end": END
        }
    )
    graph.add_edge('gad_7_scorer', END)
    graph.add_edge('phq_9_scorer', END)

    graph = graph.compile()

    return graph


medic_graph = build_graph()
