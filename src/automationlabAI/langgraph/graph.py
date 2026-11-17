from langgraph.graph import StateGraph, START, END
from src.automationlabAI.langgraph.nodes import get_llm, make_retrieve_role
from src.automationlabAI.langgraph.state import RAGState
from src.automationlabAI.langgraph.memory import checkpointer
from langgraph.prebuilt import create_react_agent


def build_graph(role) : 
  tool = make_retrieve_role(role)
  llm = get_llm()

  return create_react_agent(llm, tools=[tool], checkpointer=checkpointer)

