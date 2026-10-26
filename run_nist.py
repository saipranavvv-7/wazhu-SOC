"""Embed NIST chunks, store in Qdrant (in memory), run test searches."""
import uuid
from dataclasses import asdict
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from ingest.nist import nist_to_chunks

model = SentenceTransformer("BAAI/bge-large-en-v1.5")  # ~1.3 GB first run
client = QdrantClient(":memory:")  # later: QdrantClient(url="http://localhost:6333")


def point_id(key):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, key))


def ingest(chunks, collection):
    if not client.collection_exists(collection):
        client.create_collection(
            collection, vectors_config=VectorParams(size=1024, distance=Distance.COSINE))
    vecs = model.encode([c.text for c in chunks], normalize_embeddings=True,
                        show_progress_bar=True)
    client.upsert(collection, points=[
        PointStruct(id=point_id(f"{c.source_type}:{c.id}"), vector=v.tolist(),
                    payload=asdict(c))
        for c, v in zip(chunks, vecs)])
    print(client.count(collection).count, "points in", collection)


def search(query, collection, k=3):
    q = "Represent this sentence for searching relevant passages: " + query
    qv = model.encode(q, normalize_embeddings=True).tolist()
    print("\nQUERY:", query)
    for h in client.query_points(collection, query=qv, limit=k).points:
        print(" ", round(h.score, 3), h.payload["id"], "-", h.payload["text"][:90])


chunks = nist_to_chunks()
ingest(chunks, "nist")
ingest(chunks, "nist")  # count must NOT change
search("multiple failed ssh logins from same IP", "nist")
search("ransomware encrypted files on a server", "nist")
search("unauthorized change to a system file", "nist")
