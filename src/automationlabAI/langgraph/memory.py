from dotenv import load_dotenv
import os
from langgraph.checkpoint.postgres import PostgresSaver
import psycopg

load_dotenv()
# DB_URI = "postgres://usernma:pw@localhost:port/rag_b"
DB_NAME = str(os.getenv("DB_NAME"))
USER = str(os.getenv("POSTGRES_USER"))
PASSWORD = str(os.getenv("POSTGRES_PASSWORD"))
PORT = str(os.getenv("PORT"))
DB_URI = f"postgres://{USER}:{PASSWORD}@localhost:{PORT}/{DB_NAME}"

connection = psycopg.connect(DB_URI, autocommit=True)

checkpointer = PostgresSaver(connection)
checkpointer.setup()
"""
Objectif de memory.py

Rendre la conversation persistante entre les appels. Sans ça, chaque /ask repart de zéro — LangGraph ne se souvient de rien d'un appel à l'autre.

---

Ce que fait PostgresSaver

C'est un checkpointer — un composant qui sauvegarde l'état du graphe dans PostgreSQL après chaque nœud. Quand tu rappelles le graphe avec le même thread_id, il recharge l'état depuis la base et reprend là où il s'était arrêté.

Concrètement : c'est lui qui permet à l'utilisateur de dire "et pour lui ?" après une première question, et que le RAG comprenne le contexte.

---

Librairies à utiliser

- langgraph-checkpoint-postgres — le package qui fournit PostgresSaver
- psycopg (version 3, pas psycopg2) — PostgresSaver utilise psycopg3, pas psycopg2

pip install langgraph-checkpoint-postgres psycopg[binary]

---

Ce que tu dois implémenter dans memory.py

1. Construire la DB_URI depuis les variables d'environnement
2. Initialiser le PostgresSaver avec cette URI
3. Appeler .setup() une seule fois pour créer les tables LangGraph dans ta base
4. Exposer le checkpointer pour que graph.py puisse le passer à compile()
"""