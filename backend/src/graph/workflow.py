from langgraph.graph import StateGraph, END
from backend.src.graph.state import AgentState
from backend.src.graph.node import (
    extract_video_data_node,
    retrieve_compliance_rules_node,
    grade_documents_node,
    web_search_fallback_node,
    crag_evaluation_node
)

def route_after_grading(state: AgentState):
    if state.needs_web_search == "yes":
        return "web_search"
    else:
        return "evaluate"

workflow = StateGraph(AgentState)

workflow.add_node("extract_video", extract_video_data_node)
workflow.add_node("retrieve_rules", retrieve_compliance_rules_node)
workflow.add_node("grade_rules", grade_documents_node)
workflow.add_node("web_search", web_search_fallback_node)
workflow.add_node("evaluate", crag_evaluation_node)

workflow.set_entry_point("extract_video")

workflow.add_edge("extract_video", "retrieve_rules")
workflow.add_edge("retrieve_rules", "grade_rules")

workflow.add_conditional_edges(
    "grade_rules",
    route_after_grading,
    {
        "web_search": "web_search",
        "evaluate": "evaluate"
    }
)

workflow.add_edge("web_search", "evaluate")
workflow.add_edge("evaluate", END)

compliance_graph = workflow.compile()