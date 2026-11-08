from langgraph.graph import StateGraph, START, END
from src.automationlabAI.langgraph.nodes import langgraph_generate, langgraph_no_context, langgraph_retrieve, langgraph_rewrite
from src.automationlabAI.langgraph.state import RAGState
from src.automationlabAI.langgraph.memory import checkpointer

graph = StateGraph(RAGState)

graph.add_node("rewrite", langgraph_rewrite)
graph.add_node("retrieve", langgraph_retrieve)
graph.add_node("generate", langgraph_generate)
graph.add_node("no_context", langgraph_no_context)

graph.add_edge(START, "rewrite")
graph.add_edge("rewrite", "retrieve")
graph.add_edge("generate", END)
graph.add_edge("no_context", END)

def should_continue(state : RAGState) : 
  if len(state["context"]) == 0 :
    return "no_context"
  return "generate"

graph.add_conditional_edges("retrieve", should_continue, ["generate", "no_context"])

graph = graph.compile(checkpointer=checkpointer)
