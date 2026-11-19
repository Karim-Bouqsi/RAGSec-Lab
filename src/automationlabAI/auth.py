from dotenv import load_dotenv
import os
from jose import jwt
import bcrypt
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

ALGO = str(os.getenv("ALGO"))
SECRET_KEY = str(os.getenv("SECRET_KEY"))

def create_access_token(data) -> str :
  return jwt.encode(data, SECRET_KEY, algorithm=ALGO)

def verify_token(encoded_token) :
  return jwt.decode(encoded_token, SECRET_KEY, algorithms=[ALGO])

def hash_password(password : str) -> str :
  return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password : str, hashed_password : str) -> bool :
  return bcrypt.checkpw(password.encode(), hashed_password.encode())

def get_user_from_db(username : str) :
  cursor.execute("SELECT username, hashed_password, role FROM users where username = %s", (username,))
  return cursor.fetchone()

def get_all_users() :
  cursor.execute("SELECT username, role FROM users ORDER BY role, username")
  return cursor.fetchall()
