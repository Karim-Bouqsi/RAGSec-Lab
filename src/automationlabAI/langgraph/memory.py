from dotenv import load_dotenv
import os
from langgraph.checkpoint.postgres import PostgresSaver
import psycopg

load_dotenv()
DB_NAME = str(os.getenv("DB_NAME"))
USER = str(os.getenv("POSTGRES_USER"))
PASSWORD = str(os.getenv("POSTGRES_PASSWORD"))
PORT = str(os.getenv("PORT"))
DB_URI = f"postgres://{USER}:{PASSWORD}@localhost:{PORT}/{DB_NAME}"

connection = psycopg.connect(DB_URI, autocommit=True)

checkpointer = PostgresSaver(connection)
checkpointer.setup()