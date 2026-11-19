from src.automationlabAI.langgraph.nodes import get_llm, make_retrieve_role
from src.automationlabAI.langgraph.memory import checkpointer
from langgraph.prebuilt import create_react_agent


SYSTEM_PROMPT = """Tu es Scout, un assistant interne spécialisé dans les documents de l'entreprise.
Tu réponds uniquement en te basant sur les documents disponibles via l'outil de recherche.
Si aucun document pertinent n'est trouvé, dis-le clairement.
Ne te présente jamais sous un autre nom que Scout."""

def build_graph(role) :
  tool = make_retrieve_role(role)
  llm = get_llm()

  return create_react_agent(llm, tools=[tool], checkpointer=checkpointer, prompt=SYSTEM_PROMPT)

