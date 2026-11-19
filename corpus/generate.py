"""
Génération du corpus synthétique du Raccourci via l'API Claude Haiku 4.5.
Produit un fichier JSONL par catégorie dans corpus/data/.
"""

import anthropic
import hashlib
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
CONTEXT = """
Tu génères des documents internes pour "Le Raccourci", une agence fictive de 60 personnes spécialisée en développement web, automatisation de workflows et solutions IA pour les entreprises.
L'agence propose : création de sites et d'applications web sur-mesure, automatisation de processus métier (n8n, Make, Zapier), intégration d'IA (chatbots, agents, RAG), et publie des tutoriels et guides pratiques pour aider les entreprises à se moderniser.
Clients : PME et ETI de secteurs variés (commerce, santé, logistique, RH, finance).
Équipes : Dev web (15p), Automatisation/IA (12p), Design/UX (6p), Commercial (8p), Support client (7p), Contenu/Tutos (5p), RH/Admin (4p), Direction (3p).
Les documents doivent être réalistes, variés, et en français.
"""

CATEGORIES = {
    "rh": {
        "acl_role": "rh",
        "target": 30,
        "batch_topics": [
            "politique de congés payés, RTT et absences justifiées au Raccourci",
            "grille de salaires, révisions annuelles et primes pour une agence web/IA",
            "procédure de recrutement : offre, entretiens techniques, intégration, période d'essai",
            "règlement intérieur : horaires flexibles, télétravail total ou partiel, charte informatique",
            "avantages sociaux : mutuelle, tickets resto, forfait matériel home office, remote",
            "politique de formation : veille techno, certifications cloud/IA, budget individuel",
            "procédure disciplinaire et gestion des conflits dans une agence créative",
            "organigramme, fiches de poste (dev, automatisation, IA, commercial, support)",
        ],
        "prompt_template": (
            "Génère {n} documents RH internes distincts sur le thème suivant : {topic}.\n"
            "Chaque document doit avoir un titre, un auteur fictif (RH Le Raccourci), une date, et un contenu de 150 à 300 mots.\n"
            "Les documents doivent être variés entre eux (pas de répétition de structure ni de contenu).\n"
            "Réponds UNIQUEMENT avec un tableau JSON valide : [{{'titre': '...', 'contenu': '...'}}, ...]"
        ),
    },
    "technique": {
        "acl_role": "technique",
        "target": 80,
        "batch_topics": [
            "stack technique de l'agence : Next.js, FastAPI, PostgreSQL, Docker, déploiement VPS/cloud",
            "procédures de déploiement de sites clients sur staging et production avec rollback",
            "runbooks d'incidents : site client hors ligne, webhook cassé, automatisation bloquée",
            "guide de contribution Git : branches, commits conventionnels, PR process, code review",
            "documentation des APIs internes et des connecteurs d'automatisation (n8n, Make, Zapier)",
            "installation et configuration de l'environnement de développement local",
            "postmortems d'incidents clients : chronologie, cause racine, actions correctives",
            "conventions de code Python, TypeScript et standards de tests pour l'agence",
            "monitoring des workflows d'automatisation : alertes, logs, reprise sur erreur",
            "sécurité : gestion des clés API clients, secrets, accès aux outils tiers",
            "onboarding technique d'un nouveau développeur ou automatiseur au Raccourci",
            "bonnes pratiques pour les intégrations IA : LLM, RAG, agents, prompts systèmes",
        ],
        "prompt_template": (
            "Génère {n} documents techniques internes distincts sur le thème suivant : {topic}.\n"
            "Chaque document doit avoir un titre, un auteur fictif (équipe technique Le Raccourci), une date, et un contenu de 200 à 400 mots.\n"
            "Les documents doivent être réalistes et variés (différentes équipes, différents cas d'usage clients).\n"
            "Réponds UNIQUEMENT avec un tableau JSON valide : [{{'titre': '...', 'contenu': '...'}}, ...]"
        ),
    },
    "support": {
        "acl_role": "support",
        "target": 400,
        "batch_topics": [
            "problèmes avec un site livré : bug d'affichage, formulaire qui ne soumet pas, erreur 500",
            "automatisation bloquée : workflow n8n/Make/Zapier qui ne se déclenche plus",
            "questions sur une intégration livrée : Slack, Notion, Google Sheets, CRM",
            "demande de modification post-livraison : changement de texte, couleur, fonctionnalité",
            "questions de facturation : devis, acompte, solde, délai de paiement",
            "demande d'accès ou de formation sur un outil livré",
            "bug dans un chatbot ou agent IA livré : réponses incorrectes, hors sujet",
            "performance du site client : lenteur, score PageSpeed, optimisation images",
            "problème d'email : formulaire de contact qui n'envoie pas, notification manquante",
            "demande de nouveau projet ou extension de prestation existante",
            "questions sur les tutoriels publiés sur le site du Raccourci",
            "problème d'hébergement, nom de domaine ou certificat SSL",
        ],
        "prompt_template": (
            "Génère {n} tickets de support client distincts sur le thème suivant : {topic}.\n"
            "Chaque ticket doit avoir : un titre court, un nom de client fictif (entreprise), une date, "
            "le statut (ouvert/résolu/en cours), la priorité (basse/normale/haute/critique), "
            "et le contenu du ticket (description du problème par le client, 80 à 200 mots).\n"
            "Les tickets doivent être variés : différents clients, différentes formulations, différentes situations.\n"
            "Réponds UNIQUEMENT avec un tableau JSON valide : "
            "[{{'titre': '...', 'client': '...', 'statut': '...', 'priorite': '...', 'contenu': '...'}}, ...]"
        ),
    },
    "wiki": {
        "acl_role": "wiki",
        "target": 120,
        "batch_topics": [
            "guides pratiques de l'agence : réservation de salles, matériel, outils internes",
            "compte-rendus de réunions d'équipe dev, automatisation et direction",
            "FAQ interne : questions fréquentes des nouveaux arrivants au Raccourci",
            "pages projet par équipe : roadmap, objectifs trimestriels, rétrospectives",
            "glossaire métier : termes web, automatisation, IA, acronymes internes",
            "bonnes pratiques : communication client, gestion de projet agile, documentation",
            "ressources accessibles à tous : annuaire, organigramme, contacts utiles",
            "événements et vie d'agence : team buildings, veille techno, afterworks",
            "outils et licences de l'agence : Figma, Linear, Notion, Slack, accès et guides",
            "processus transverses : gestion des congés, notes de frais, livraison client",
        ],
        "prompt_template": (
            "Génère {n} pages de wiki interne distincts sur le thème suivant : {topic}.\n"
            "Chaque page doit avoir un titre, un auteur fictif (membre du Raccourci), une date de dernière modification, "
            "et un contenu de 150 à 300 mots.\n"
            "Les pages doivent être variées et réalistes, comme un vrai wiki d'agence web/IA.\n"
            "Réponds UNIQUEMENT avec un tableau JSON valide : [{{'titre': '...', 'auteur': '...', 'contenu': '...'}}, ...]"
        ),
    },
}


def load_existing_hashes(category: str) -> set[str]:
    path = DATA_DIR / f"{category}.jsonl"
    if not path.exists():
        return set()
    hashes = set()
    with open(path) as f:
        for line in f:
            doc = json.loads(line)
            hashes.add(doc["hash"])
    return hashes


def hash_content(content: str) -> str:
    return hashlib.sha256(content.strip().encode()).hexdigest()[:16]


def generate_batch(prompt: str, retries: int = 3) -> list[dict]:
    for attempt in range(retries):
        try:
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=8192,
                messages=[
                    {"role": "user", "content": CONTEXT + "\n\n" + prompt}
                ],
            )
            raw = response.content[0].text.strip()
            # Extraire le tableau JSON quelle que soit la mise en forme (markdown ou non)
            match = re.search(r"\[.*\]", raw, re.DOTALL)
            if not match:
                print(f"  ⚠ Pas de JSON trouvé, tentative {attempt + 1}/{retries}")
                print(f"     Réponse reçue : {raw[:300]}")
                continue
            return json.loads(match.group())
        except (json.JSONDecodeError, anthropic.APIError) as e:
            print(f"  ⚠ Erreur tentative {attempt + 1}/{retries} : {e}")
            time.sleep(2 ** attempt)
    return []


def save_documents(category: str, docs: list[dict], existing_hashes: set[str]) -> int:
    path = DATA_DIR / f"{category}.jsonl"
    cat_config = CATEGORIES[category]
    saved = 0
    with open(path, "a") as f:
        for doc in docs:
            content = doc.get("contenu", "")
            if not content:
                continue
            h = hash_content(content)
            if h in existing_hashes:
                continue
            existing_hashes.add(h)
            record = {
                "id": f"{category}_{h}",
                "hash": h,
                "source": category,
                "acl_role": cat_config["acl_role"],
                "titre": doc.get("titre", "Sans titre"),
                "content": content,
                "metadata": {k: v for k, v in doc.items() if k not in ("titre", "contenu")},
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            saved += 1
    return saved


def count_existing(category: str) -> int:
    path = DATA_DIR / f"{category}.jsonl"
    if not path.exists():
        return 0
    with open(path) as f:
        return sum(1 for _ in f)


def generate_category(category: str) -> None:
    config = CATEGORIES[category]
    target = config["target"]
    topics = config["batch_topics"]
    prompt_template = config["prompt_template"]

    existing = count_existing(category)
    existing_hashes = load_existing_hashes(category)
    print(f"\n{'='*50}")
    print(f"Catégorie : {category.upper()} | Cible : {target} | Existants : {existing}")

    if existing >= target:
        print("  ✓ Cible déjà atteinte, on passe.")
        return

    topic_idx = 0
    while count_existing(category) < target:
        current = count_existing(category)
        remaining = target - current
        batch_size = min(10, remaining)
        topic = topics[topic_idx % len(topics)]
        topic_idx += 1

        prompt = prompt_template.format(n=batch_size, topic=topic)
        print(f"  → {current}/{target} | Thème : {topic[:60]}...")

        docs = generate_batch(prompt)
        saved = save_documents(category, docs, existing_hashes)
        print(f"    Reçu : {len(docs)} | Sauvegardé (sans doublons) : {saved}")

        time.sleep(0.5)  # Rate limiting léger


def main() -> None:
    print("Génération du corpus Le Raccourci")
    print(f"Sortie : {DATA_DIR}")

    categories_to_generate = list(CATEGORIES.keys())
    for category in categories_to_generate:
        generate_category(category)

    print("\n" + "="*50)
    print("Résumé final :")
    total = 0
    for cat in CATEGORIES:
        n = count_existing(cat)
        total += n
        print(f"  {cat:12} : {n:4} documents")
    print(f"  {'TOTAL':12} : {total:4} documents")


if __name__ == "__main__":
    main()
