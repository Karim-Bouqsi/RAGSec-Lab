from langchain_core.messages import HumanMessage
from pydantic import BaseModel
from src.automationlabAI.langgraph.graph import graph
from src.automationlabAI.embed import encode
from src.automationlabAI.indexer import insert_document

import uuid

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from src.automationlabAI.auth import create_access_token, get_user_from_db, verify_password, verify_token


app = FastAPI(title="API AutomationLabAI", version="1.0.0")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


class QueryRequest(BaseModel) : 
  question : str
  conversation_id : str

class LoginRequest(BaseModel) : 
  username : str
  password : str

class IndexRequest(BaseModel) : 
  content : str
  source : str
  acl_role : str


@app.post("/conversation")
async def new_conversation(token : str=Depends(oauth2_scheme)) :
  payload = verify_token(token)
  username = payload.get("username")
  if not username : 
    raise HTTPException(status_code=401, detail="Token invalide")
  
  conversation_id = str(uuid.uuid4())
  thread_id = f"{username}-{conversation_id}"
  return {"conversation_id" : conversation_id, "thread_id" : thread_id}

@app.post("/ask")
async def ask(request : QueryRequest, token : str=Depends(oauth2_scheme)) : 
  payload = verify_token(token)
  role = payload.get("role")

  if not role : 
    raise HTTPException(status_code=401, detail="Token invalide")
  
  username = payload.get("username")
  thread_id = f"{username}-{request.conversation_id}"
  config = {"configurable" : {"thread_id" : thread_id}}

  rag_response = graph.invoke({"messages" : [HumanMessage(request.question)], "role" : role, "context" : [], "rewritten_query" : None}, config)
  return {"response" : rag_response["messages"][-1].content}

# graph.invoke({"messages": [HumanMessage("Combien de congés ?")], "role": "rh", "context": []}, config)

@app.post("/login")
async def login(request : LoginRequest) : 
  user = get_user_from_db(request.username)
  if not user : 
    raise HTTPException(status_code=401)

  check_password = verify_password(request.password, user[1])
  if not check_password : 
    raise HTTPException(status_code=401, detail="Identifiants invalides")

  token = create_access_token({"username" : user[0], "role" : user[2]})

  return {"access_token" : token}


@app.post("/index")
async def index(request : IndexRequest, token : str=Depends(oauth2_scheme)) : 
  payload = verify_token(token)
  role = payload.get("role")
  if not role or role != "admin" : 
    raise HTTPException(status_code=401, detail="Token invalide")

  embedding = str(encode(request.content))
  insert_document((request.content, embedding, request.source, request.acl_role))

  return {"message" : "Document indéxé avec succès"}