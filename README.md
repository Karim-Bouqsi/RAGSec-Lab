# RAGSec-Lab

Système RAG d'entreprise avec interface de chat, gestion de conversations, contrôle d'accès par rôle (ACL), et module d'attaques pour la recherche en sécurité IA.

## Stack technique

| Composant | Technologie |
|---|---|
| LLM | DeepSeek via OpenRouter |
| Orchestration | LangGraph (ReAct agent) |
| Mémoire | PostgresSaver (psycopg3) |
| Base de données | PostgreSQL + pgvector |
| Backend | FastAPI |
| Frontend | HTML / CSS / JS (vanilla) |
| Embeddings | sentence-transformers |

## Architecture

```
RAGSec-Lab/
├── corpus/
│   ├── data/              # Documents sources (rh, technique, support, wiki)
│   ├── generated/         # Résultats générés (ignorés par git)
│   ├── generate.py        # Génération du corpus synthétique
│   └── generate_dataset.py
├── src/automationlabAI/
│   ├── api.py             # Endpoints FastAPI
│   ├── auth.py            # JWT + gestion utilisateurs (psycopg2)
│   ├── embed.py           # Encodage des embeddings
│   ├── indexer.py         # Insertion en base pgvector
│   ├── retriever.py       # Recherche par similarité cosinus + ACL
│   └── langgraph/
│       ├── graph.py       # Agent ReAct (create_react_agent)
│       ├── memory.py      # PostgresSaver checkpointer
│       ├── nodes.py       # LLM + outil de recherche
│       └── state.py       # RAGState
└── src/automationlabAI/static/
    ├── index.html         # Sélecteur de profils
    ├── chat.html          # Interface de chat
    ├── admin.html         # Interface d'indexation
    ├── style.css
    └── app.js
```

## Prérequis

- Python 3.10+
- PostgreSQL avec extension pgvector
- Compte OpenRouter (clé API)

## Installation

```bash
# 1. Cloner le dépôt
git clone https://github.com/Karim-Bouqsi/RAGSec-Lab.git
cd RAGSec-Lab

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Configurer les variables d'environnement
cp .env.example .env
# Remplir .env avec vos valeurs

# 4. Lancer PostgreSQL (Docker)
docker compose up -d

# 5. Indexer le corpus
python corpus/generate.py

# 6. Démarrer le serveur
uvicorn src.automationlabAI.api:app --reload
```

L'interface est accessible sur `http://localhost:8000`.

## Profils disponibles

| Utilisateur | Rôle | Accès corpus |
|---|---|---|
| Karim | rh | Documents RH |
| Redouane | technique | Documents techniques |
| Armand | support | Documents support |
| Kylian | wiki | Wiki interne |

Usage local — aucun mot de passe requis, sélection directe du profil.

## Fonctionnalités

- **Multi-conversations** : historique persistant par utilisateur dans PostgreSQL
- **ACL** : chaque utilisateur accède uniquement aux documents de son rôle
- **Mémoire contextuelle** : LangGraph checkpointer, contexte maintenu entre les messages
- **Admin** : interface d'indexation de documents à la volée

## Attaques implémentées

Voir `src/automationlabAI/` — module d'attaques sur le RAG :

| ID | Type |
|---|---|
| A1 | Prompt injection |
| A2 | Data poisoning |
| A3 | Data extraction |
| A4 | ACL bypass |
| A5 | Jailbreak |
| A6 | DoS sémantique |

## Variables d'environnement

Voir `.env.example` pour la liste complète des variables requises.
