from langchain_core.messages import AIMessage
import ollama

from src.automationlabAI.langgraph.state import RAGState
from src.automationlabAI.retriever import retrieve



def langgraph_retrieve(state : RAGState) :
  question = state["rewritten_query"]
  
  role = state["role"]

  docs = retrieve(question, role)

  return {"context" : docs}


def langgraph_generate(state : RAGState) : 
  context = state["context"]
  messages = state["messages"]

  system_prompt = "Tu est un assistant qui répond uniquement sur les documents qui lui sont fournis"

  response = ollama.chat(model="qwen2.5:3b", messages=[{"role" : "system", "content" : f"{system_prompt}\n\nDocuments :\n{context}"}] + [
    {"role" : message.type, "content" : message.content} for message in messages
  ])

  return {"messages" : [AIMessage(content=response.message.content)]}

def langgraph_no_context(state : RAGState) : 
  return {"messages" : [AIMessage(content="Je n'ai pas l'information dans les documents disponibles")]}


def langgraph_rewrite(state : RAGState) : 
  messages = state["messages"]

  system = f"""System: Tu reformules la dernière question de l'utilisateur en une question autonome complète, en tenant compte du contexte de la conversation. Réponds UNIQUEMENT avec la question reformulée. Historique : {messages}]"""
  response = ollama.chat(model="qwen2.5:3b", messages=[{"role" : "system", "content" : f"{system}\n\nHistorique :\n"}] + [
    {"role" : message.type, "content" : message.content} for message in messages
  ])

  return {"rewritten_query" : response.message.content}