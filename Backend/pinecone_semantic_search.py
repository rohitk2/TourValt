# semantic_search.py
import os
import argparse
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

INDEX_NAME = "youtube-transcripts"   # same index you used to insert
MODEL_NAME = "all-MiniLM-L6-v2"      # dim=384

def ensure_index(pc: Pinecone, name: str):
    names = pc.list_indexes().names()
    if name not in names:
        raise RuntimeError(
            f"Index '{name}' not found. Available: {list(names)}"
        )
    return pc.Index(name)

def search(query: str, top_k: int = 5):
    # init
    pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
    index = ensure_index(pc, INDEX_NAME)
    model = SentenceTransformer(MODEL_NAME)

    # embed the query
    q_vec = model.encode(query).tolist()

    # query pinecone
    res = index.query(vector=q_vec, top_k=top_k, include_metadata=True)

    # print results
    print(f"\nQuery: {query}\nTop {top_k} results:\n")
    for i, match in enumerate(res.matches, start=1):
        md = match.metadata or {}
        title = md.get("title", "<no title>")
        snippet = (md.get("content", "")[:120] + "...") if md.get("content") else ""
        print(f"{i}. title: {title}\n   id: {match.id}\n   score: {match.score:.4f}\n   snippet: {snippet}\n")

search("I always forget to hit record Property tour abord team Zuber and Associates super pumped hey guys how's it going there he is hey hey how's it going awesome I so stoked to shoot man I get to put my camera away that's what I'm talking about good I did my hair today yeah bro good to see you man good to see you I got to grab my jacket wor and then do you know where we're going um 98 cool cool cool I'm just parked over there I'll go grab my jacket yeah no worries and then I'll head over there and the")

