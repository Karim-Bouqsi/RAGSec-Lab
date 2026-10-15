from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from src.automationlabAI.rag import main

app = FastAPI(title="API AutomationLabAI", version="1.0.0")

class QueryRequest(BaseModel) : 
  question : str
  role : str

@app.post("/ask")
async def ask(request : QueryRequest) : 
  rag_response = main(request.question, request.role)

  return {
    "response" : rag_response
  }