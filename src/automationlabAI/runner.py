from pathlib import Path

import requests


import json


def runner(document_path, new_document_path) : 
  with document_path.open(encoding="utf-8") as f : 
    for line_number, line in enumerate(f, 1) : 
      line = line.strip()
      if not line : 
        continue

      try : 
        data = json.loads(line)

        question = data.get("question")
        role = data.get("role")

        payload = {
          "question" : question,
          "role" : role
        }
        response = requests.post(url="http://localhost:8000/ask", json=payload)
        if response.status_code == 200 : 
          data["actual_answer"] = response.json()["response"]
          with open(new_document_path, 'a', encoding="utf-8") as f : 
            f.write(json.dumps(data) + "\n")
            
      except json.JSONDecodeError as error :
          print(f"Erreur JSON à la ligne {line_number} de {f.name} : {error}")




if __name__ == "__main__" :
    base = Path(__file__).parent.parent.parent / "corpus"
    runner(base / "dataset.jsonl", base / "results.jsonl")