from src.automationlabAI.embed import encode
import os
from dotenv import load_dotenv
import psycopg2


load_dotenv()


connection = psycopg2.connect(
  dbname=str(os.getenv("DB_NAME")),
  user=str(os.getenv("POSTGRES_USER")),
  password=str(os.getenv("POSTGRES_PASSWORD")),
  host="localhost",
  port=str(os.getenv("PORT"))
)

cursor = connection.cursor()



def retrieve(prompt : str, acl_role : str, top_k=3) : 
  prompt_embedding = encode(prompt)

  req = "SELECT content FROM documents WHERE acl_role = %s ORDER BY embedding <=> %s LIMIT %s"

  cursor.execute(req, (acl_role, str(prompt_embedding), top_k))

  best_documents = cursor.fetchall()

  return best_documents


if __name__ == "__main__" : 
  results = retrieve("politique de congés", "rh")
  for doc in results:
      print(doc[0][:200])
      print("---")