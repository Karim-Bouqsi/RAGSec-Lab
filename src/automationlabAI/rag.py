import ollama

from src.automationlabAI.retriever import retrieve

def main(question, role) :
  docs = retrieve(question, role)
  prompt = f"Documents : \n {docs}\n Question : {question}\n"

  response = ollama.chat(model="qwen2.5:3b", messages=[{"role" : "user", "content" : prompt}])

  return response.message.content


