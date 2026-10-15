

import json
import os
from pathlib import Path
import re
from dotenv import load_dotenv
import anthropic
load_dotenv()

PROMPT_SYSTEM = """
Tu es un juge qui évalue la qualité d'une réponse RAG.\
On te donne une question, une réponse attendue et une réponse réelle.\
Tu dois retourner UNIQUEMENT un JSON valide : {"score": 0 ou 1, "justification": "..."} \
Score 1 = la réponse réelle est fidèle et correcte par rapport à la réponse attendue. \
Score 0 = la réponse est incorrecte, incomplète ou inventée.
"""
client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

def judge(document_path, score_result_path) : 
  with document_path.open(encoding="utf-8") as f : 
    for line_number, line in enumerate(f, 1) : 
      line = line.strip()
      if not line : 
        continue

      try : 
        data = json.loads(line)

        question = data.get("question")
        expected_answer = data.get("expected_answer")
        actual_answer = data.get("actual_answer")

        content = f"Question : {question}\nRéponse attendue : {expected_answer}\nRéponse réelle : {actual_answer}"
        messages = [{"role" : "user", "content" : content}]
        response = client.messages.create(
            model="claude-haiku-5-5",
            system=PROMPT_SYSTEM,
            messages=messages,
            max_tokens=1024
        )

        text_block = next((b for b in response.content if hasattr(b, "text") and b.text), None)
        if not text_block :
            print(f"Pas de bloc texte ligne {line_number}, ignoré")
            continue
        raw = text_block.text.strip()
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            print(f"  ⚠ Pas de JSON ligne {line_number}, ignoré")
            continue

        infos = json.loads(match.group())

        score = infos.get("score")
        justification = infos.get("justification")

        data["score"] = score
        data["justification"] = justification

        with open(score_result_path, "a", encoding="utf-8") as out : 
          out.write(json.dumps(data, ensure_ascii=False) + "\n")

      except json.JSONDecodeError as error : 
        print(f"Erreur JSON à la ligne {line_number} : {error}")


if __name__ == "__main__" : 
    base = Path(__file__).parent.parent.parent / "corpus"
    judge(base / "results.jsonl", base / "judge_results.jsonl")