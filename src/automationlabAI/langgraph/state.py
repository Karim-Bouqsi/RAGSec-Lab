from langgraph.graph import MessagesState
from typing import Optional

class RAGState(MessagesState) : 
  context : list[str]
  role : str
  rewritten_query : Optional[str] = None

