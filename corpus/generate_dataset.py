"""
Génération du dataset d'évaluation pour le harnais RAGSec.
Produit corpus/dataset.jsonl avec question, expected_answer, role, category.
"""

import anthropic
import json
import os
import random
import re
import time
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

DATA_DIR = Path(__file__).parent / "data"
OUTPUT_FILE = Path(__file__).parent / "dataset.jsonl"

SAMPLES_PER_CATEGORY = {
    "rh": 30,
    "technique": 40,
    "support": 50,
    "wiki": 30,
}

PROMPT_TEMPLATE = """Tu génères une paire (question, réponse attendue) pour évaluer un assistant RAG interne.

Voici un document interne de l'agence "Le Raccourci" :
---
{content}
---

Génère UNE question précise qu'un employé pourrait poser à l'assistant, et la réponse attendue basée UNIQUEMENT sur ce document.
La réponse doit être fidèle au document, concise (2-5 phrases), et ne pas inventer d'informations.

Réponds UNIQUEMENT avec un objet JSON valide : {{"question": "...", "expected_answer": "..."}}"""


def load_documents(category: str) -> list[dict]:
    path = DATA_DIR / f"{category}.jsonl"
    docs = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                docs.append(json.loads(line))
    return docs


def generate_qa_pair(content: str, retries: int = 3) -> dict | None:
    for attempt in range(retries):
        try:
            response = client.messages.create(
                model="claude-haiku-5-5",
                max_tokens=512,
                messages=[{"role": "user", "content": PROMPT_TEMPLATE.format(content=content[:2000])}],
            )
            text_block = next((b for b in response.content if hasattr(b, "text")), None)
            if not text_block:
                print(f"  ⚠ Pas de bloc texte, tentative {attempt + 1}/{retries}")
                continue
            raw = text_block.text.strip()
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if not match:
                print(f"  ⚠ Pas de JSON, tentative {attempt + 1}/{retries}")
                continue
            return json.loads(match.group())
        except (json.JSONDecodeError, anthropic.APIError) as e:
            print(f"  ⚠ Erreur tentative {attempt + 1}/{retries} : {e}")
            time.sleep(2 ** attempt)
    return None


def main() -> None:
    print("Génération du dataset d'évaluation")
    print(f"Sortie : {OUTPUT_FILE}")

    total = 0
    with open(OUTPUT_FILE, "w") as out:
        for category, n_samples in SAMPLES_PER_CATEGORY.items():
            docs = load_documents(category)
            sample = random.sample(docs, min(n_samples, len(docs)))
            print(f"\n{'='*50}")
            print(f"Catégorie : {category.upper()} | {n_samples} questions")

            saved = 0
            for i, doc in enumerate(sample):
                content = doc.get("content", "")
                if not content:
                    continue

                print(f"  → {i + 1}/{n_samples} | {doc.get('titre', '')[:60]}...")
                qa = generate_qa_pair(content)

                if not qa or not qa.get("question") or not qa.get("expected_answer"):
                    print("    ⚠ Ignoré (réponse invalide)")
                    continue

                record = {
                    "question": qa["question"],
                    "expected_answer": qa["expected_answer"],
                    "role": doc.get("acl_role", category),
                    "category": category,
                    "source_doc_id": doc.get("id", ""),
                }
                out.write(json.dumps(record, ensure_ascii=False) + "\n")
                saved += 1
                time.sleep(0.2)

            print(f"  ✓ {saved}/{n_samples} paires générées")
            total += saved

    print(f"\n{'='*50}")
    print(f"Dataset final : {total} paires → {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
