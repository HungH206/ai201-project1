#!/usr/bin/env python3
"""Embed Project 1 chunks into ChromaDB and test retrieval."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import textwrap
from pathlib import Path
from typing import Any

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CHUNKS_PATH = PROJECT_ROOT / "documents" / "chunks" / "chunks.jsonl"
CHROMA_DIR = PROJECT_ROOT / "vector_store" / "chroma"
RETRIEVAL_REPORT_PATH = PROJECT_ROOT / "documents" / "chunks" / "retrieval_report.json"
COLLECTION_NAME = "uh_dining_chunks"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
DEFAULT_TOP_K = 5

EVALUATION_QUERIES = [
    "What are the breakfast items at Chick-fil-A?",
    "What entree items are available at Panda Express?",
    "Does The Burger Joint have any alcoholic root beer?",
    "Are there any dining halls at the University of Houston?",
    "Is there a commuter meal plan?",
]


def load_embedding_model() -> SentenceTransformer:
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
    try:
        return SentenceTransformer(EMBEDDING_MODEL_NAME, local_files_only=True)
    except TypeError:
        return SentenceTransformer(EMBEDDING_MODEL_NAME)


def load_chunks(path: Path = CHUNKS_PATH) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(
            f"Missing chunks file: {path}. Run scripts/ingest_and_chunk.py first."
        )

    chunks = []
    with path.open("r", encoding="utf-8") as input_file:
        for line_number, line in enumerate(input_file, start=1):
            if not line.strip():
                continue
            chunk = json.loads(line)
            required = {"chunk_id", "source_title", "source_url", "chunk_index", "text"}
            missing = required - set(chunk)
            if missing:
                raise ValueError(f"Chunk line {line_number} is missing keys: {sorted(missing)}")
            chunks.append(chunk)

    if not chunks:
        raise ValueError(f"No chunks found in {path}")
    return chunks


def get_chroma_collection(reset: bool = False):
    if reset and CHROMA_DIR.exists():
        shutil.rmtree(CHROMA_DIR)

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(
        path=str(CHROMA_DIR),
        settings=Settings(anonymized_telemetry=False),
    )
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def build_metadata(chunk: dict[str, Any]) -> dict[str, str | int]:
    return {
        "source_slug": str(chunk.get("source_slug", "")),
        "source_title": str(chunk["source_title"]),
        "source_url": str(chunk["source_url"]),
        "chunk_index": int(chunk["chunk_index"]),
        "token_count": int(chunk.get("token_count", 0)),
    }


def build_index(reset: bool = True) -> None:
    chunks = load_chunks()
    model = load_embedding_model()
    collection = get_chroma_collection(reset=reset)

    ids = [str(chunk["chunk_id"]) for chunk in chunks]
    documents = [str(chunk["text"]) for chunk in chunks]
    metadatas = [build_metadata(chunk) for chunk in chunks]

    print(f"Embedding {len(chunks)} chunks with {EMBEDDING_MODEL_NAME}...")
    embeddings = model.encode(
        documents,
        batch_size=32,
        show_progress_bar=True,
        normalize_embeddings=True,
    ).tolist()

    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )
    print(f"Stored {collection.count()} chunks in Chroma collection '{COLLECTION_NAME}'.")
    print(f"Vector store path: {CHROMA_DIR.relative_to(PROJECT_ROOT)}")


def retrieve(query: str, top_k: int = DEFAULT_TOP_K) -> list[dict[str, Any]]:
    model = load_embedding_model()
    collection = get_chroma_collection(reset=False)
    if collection.count() == 0:
        raise ValueError("Chroma collection is empty. Run with --index first.")

    query_embedding = model.encode(
        [query],
        normalize_embeddings=True,
    ).tolist()[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    retrieved = []
    ids = results.get("ids", [[]])[0]
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]
    for result_id, document, metadata, distance in zip(ids, documents, metadatas, distances):
        retrieved.append(
            {
                "chunk_id": result_id,
                "text": document,
                "metadata": metadata,
                "distance": distance,
            }
        )
    return retrieved


def print_results(query: str, results: list[dict[str, Any]]) -> None:
    print("\n" + "=" * 100)
    print(f"Query: {query}")
    print("=" * 100)
    for rank, result in enumerate(results, start=1):
        metadata = result["metadata"]
        preview = textwrap.shorten(result["text"], width=700, placeholder=" ...")
        print(
            f"\n#{rank} distance={result['distance']:.4f} "
            f"id={result['chunk_id']} "
            f"source={metadata.get('source_title')} "
            f"chunk={metadata.get('chunk_index')}"
        )
        print(f"url={metadata.get('source_url')}")
        print(textwrap.fill(preview, width=100))


def run_tests(top_k: int = DEFAULT_TOP_K, save_report: bool = True) -> None:
    report = []
    for query in EVALUATION_QUERIES:
        results = retrieve(query, top_k=top_k)
        print_results(query, results)
        report.append({"query": query, "top_k": top_k, "results": results})

    if save_report:
        RETRIEVAL_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        RETRIEVAL_REPORT_PATH.write_text(
            json.dumps(report, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        print(f"\nSaved retrieval report to {RETRIEVAL_REPORT_PATH.relative_to(PROJECT_ROOT)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", action="store_true", help="Embed chunks and write ChromaDB.")
    parser.add_argument(
        "--no-reset",
        action="store_true",
        help="Do not delete the existing Chroma collection before indexing.",
    )
    parser.add_argument("--query", help="Run retrieval for one query.")
    parser.add_argument("--test", action="store_true", help="Run retrieval test queries.")
    parser.add_argument("--top-k", type=int, default=DEFAULT_TOP_K, help="Number of chunks to retrieve.")
    args = parser.parse_args()

    if args.index:
        build_index(reset=not args.no_reset)

    if args.query:
        print_results(args.query, retrieve(args.query, top_k=args.top_k))

    if args.test:
        run_tests(top_k=args.top_k)

    if not (args.index or args.query or args.test):
        parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
