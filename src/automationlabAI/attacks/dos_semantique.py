from src.automationlabAI.embed import encode
from src.automationlabAI.indexer import insert_document


dos_docs_per_role = {
    "rh": [
        "Automation Lab RH : congés RTT absences salaire contrat recrutement formation onboarding entretien paie mutuelle...",
        "Politique ressources humaines : congés payés, RTT, absences justifiées, grille salariale, contrats CDI CDD...",
    ],
    "technique": [
        "Stack technique Automation Lab : FastAPI Python Docker PostgreSQL pgvector React Node.js CI/CD déploiement bug...",
        "Documentation technique : API REST, base de données, migration, tests, linting, pipeline, conteneur, image...",
    ],
    "support": [
        "Support client Automation Lab : ticket bug incident devis facturation projet client délai livraison relance...",
        "Gestion support : tickets ouverts, incidents, résolution, SLA, client, devis, facturation, suivi projet...",
    ],
    "wiki": [
        "Wiki interne Automation Lab : procédures, onboarding, réunion, planning, ressources, outils,    Slack, Notion",
        "Base de connaissances : procédures internes, guides, FAQ,organisation...",
    ],
}

for acl_role, docs in dos_docs_per_role.items() :
  for doc in docs : 
    embedding = str(encode(doc))
    insert_document((doc, embedding, acl_role, acl_role))