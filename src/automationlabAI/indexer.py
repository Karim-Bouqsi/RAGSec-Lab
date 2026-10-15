from pathlib import Path
import psycopg2
from dotenv import load_dotenv
import os
import json
from src.automationlabAI.embed import encode


load_dotenv()

connection = psycopg2.connect(
  dbname=str(os.getenv("DB_NAME")),
  user=str(os.getenv("POSTGRES_USER")),
  password=str(os.getenv("POSTGRES_PASSWORD")),
  host="localhost",
  port=str(os.getenv("PORT"))
)

cursor = connection.cursor()

def insert_document(insert_data : tuple) : 
  req = "INSERT INTO documents (content, embedding, source, acl_role) VALUES (%s, %s, %s, %s);"

  try : 
    content, embedding, source, acl_role = insert_data
    cursor.execute(req, (content, str(embedding), source, acl_role))
    connection.commit()

  except psycopg2.Error as error : 
    connection.rollback()
    print(f"Erreur PostgreSQL lors de l'insertion : {error}")



def indexer_documents(documents_path) : 
  for file in documents_path.iterdir() : 
    name = file.name


    print(f"Traitement : {name}")

    with file.open(encoding="utf-8") as f : 
      for line_number, line in enumerate(f, 1) : 
        line = line.strip()
        if not line : 
          continue

        try : 

          data_dict = json.loads(line)

          content = data_dict.get("content")
          source = data_dict.get("source")
          acl_role = data_dict.get("acl_role")

          embeded_content = str(encode(content))

          insert_data = (content, embeded_content, source, acl_role)

          insert_document(insert_data)
        except json.JSONDecodeError as error :
          print(f"Erreur JSON à la ligne {line_number} de {file.name} : {error}")


if __name__ == "__main__" : 
  data = Path(__file__).parent.parent / "corpus" / "data"

  indexer_documents(data)