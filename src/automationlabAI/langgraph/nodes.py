import os

from langchain_core.messages import AIMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from src.automationlabAI.langgraph.state import RAGState
from src.automationlabAI.retriever import retrieve
from dotenv import dotenv_values


def get_llm() :
  config = dotenv_values("/home/karim/Documents/RAGSec-Lab/.env")
  return ChatOpenAI(
      base_url="https://openrouter.ai/api/v1",
      api_key=config.get("OPENROUTER_API_KEY"),
      model="deepseek/deepseek-chat"
  )

def make_retrieve_role(role : str) : 
  @tool
  def retrieve_docs(query : str) : 
    """Recherche des documents pertinents dans la base de connaissance interne."""
    return str(retrieve(query, role))
  return retrieve_docs
