from pydantic import BaseModel, Field
from src.automationlabAI.rag import main


from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from src.automationlabAI.auth import create_access_token, get_user_from_db, verify_password, verify_token


app = FastAPI(title="API AutomationLabAI", version="1.0.0")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


class QueryRequest(BaseModel) : 
  question : str

class LoginRequest(BaseModel) : 
  username : str
  password : str


@app.post("/ask")
async def ask(request : QueryRequest, token : str=Depends(oauth2_scheme)) : 

  payload = verify_token(token)
  role = payload.get("role")
  if not role : 
    raise HTTPException(status_code=401, detail="Token invalide")

  rag_response = main(request.question, role)
  return {"response" : rag_response}

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