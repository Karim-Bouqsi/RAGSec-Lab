from sentence_transformers import SentenceTransformer

model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")


def encode(text : str) -> list[float] : 
  embeddings = model.encode(text)
  return embeddings.tolist()
