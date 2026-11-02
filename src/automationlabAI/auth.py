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

FAKE_USERS = {
    "Karim": {"password": "rh123", "role": "rh"},
    "Redouane": {"password": "tech123", "role": "technique"},
    "Armand": {"password": "support123", "role": "support"},
    "Kylian": {"password": "admin123", "role": "wiki"},
}

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














"""
Dans api.py :

5. LoginRequest ligne 15 — le role ne doit pas être dans le body. C'est précisément ce qu'on veut éviter — le rôle vient de la DB, pas du client.

6. /ask ligne 21 — le if () est vide, à remplacer par la vraie logique d'extraction du token.

7. /login ligne 32 — token_expiration vide.

Commence par corriger auth.py — les trois fonctions. Ensuite on fait api.py.

"""