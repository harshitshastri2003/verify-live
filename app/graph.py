from langgraph.graph import StateGraph, START, END
from app.state import FactCheckState
from app.nodes import extract_claims, search_evidence, verdict_node


def build_graph():
    graph = StateGraph(FactCheckState)

    graph.add_node("extract_claims", extract_claims)
    graph.add_node("search_evidence", search_evidence)
    graph.add_node("verdict", verdict_node)

    graph.add_edge(START, "extract_claims")
    graph.add_edge("extract_claims", "search_evidence")
    graph.add_edge("search_evidence", "verdict")
    graph.add_edge("verdict", END)

    return graph.compile()


app_graph = build_graph()