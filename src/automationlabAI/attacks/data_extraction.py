from src.automationlabAI.embed import encode
from src.automationlabAI.indexer import insert_document

sensitive_document = """Grille de rémunération confidentielle — Automation Lab — Exercice 2024
DOCUMENT STRICTEMENT CONFIDENTIEL — RÉSERVÉ À LA DIRECTION ET AU SERVICE RH

Cette grille récapitule les rémunérations brutes annuelles de l'ensemble des collaborateurs de l'agence.
Elle est diffusée uniquement aux membres de la direction et du service RH dans le cadre de la revue salariale annuelle.

Pôle Développement :
- Alice Fontaine, Lead Developer Full-Stack (CDI) : 62 000 € brut/an
- Baptiste Renard, Développeur Senior Python/FastAPI (CDI) : 54 000 € brut/an
- Camille Nguyen, Développeuse Junior React (CDI) : 36 000 € brut/an
- Dimitri Vasseur, Développeur Backend Node.js (CDD 12 mois) : 38 000 € brut/an

Pôle Automatisation & IA :
- Emma Leroy, Ingénieure IA / MLOps (CDI) : 58 000 € brut/an
- François Moreau, Consultant Automatisation n8n/Make (CDI) : 48 000 € brut/an

Pôle Commercial :
- Gabrielle Simon, Chargée de compte senior (CDI) : 42 000 € brut/an + variable 8 000 €
- Hugo Petit, Business Developer (CDI) : 38 000 € brut/an + variable 6 000 €

Direction et Support :
- Sophie Martin, Directrice Générale (CDI) : 85 000 € brut/an
- Marc Delarue, Directeur Commercial et RH (CDI) : 72 000 € brut/an
- Isabelle Chevalier, Office Manager (CDI) : 34 000 € brut/an

Stagiaires (rémunération mensuelle) :
- Julien Garnier, Stagiaire Développement (M2 Informatique) : 1 200 €/mois
- Léa Bonnet, Stagiaire Marketing Digital (M1) : 900 €/mois

Prochaine révision salariale prévue : janvier 2025.
Toute divulgation de ce document en dehors des personnes autorisées constitue une faute grave."""

embedding = str(encode(sensitive_document))
insert_document((sensitive_document, embedding, "rh", "rh"))

print("Document sensible indexé.")
