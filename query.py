"""Grounded RAG query function for the UH dining guide."""

from __future__ import annotations

import argparse
import os
from typing import Any

from dotenv import load_dotenv
from groq import Groq

from scripts.embed_and_retrieve import DEFAULT_TOP_K, retrieve


MODEL_NAME = "llama-3.3-70b-versatile"
MAX_CONTEXT_CHARS_PER_CHUNK = 3200
MAX_CONTEXT_DISTANCE = 0.65
MAX_CONTEXT_CHUNKS = 3
MAX_DISTANCE_FROM_BEST = 0.08

SYSTEM_PROMPT = """You are a grounded question-answering assistant for a University of Houston dining RAG system.

Rules:
- Answer using only the provided retrieved documents.
- Do not use outside knowledge, assumptions, or guesses.
- Do not explain using brand knowledge, common knowledge, or facts that are not directly stated in the retrieved text.
- If the retrieved documents do not contain enough information, answer exactly: "I don't have enough information on that."
- Give a complete answer from the retrieved text. If the question asks for items, list all relevant items found in the retrieved text with useful details such as price, calories, or notes when available.
- Keep the answer factual and avoid filler.
- Do not invent source names or URLs.
"""


def format_context(chunks: list[dict[str, Any]]) -> str:
    sections = []
    for index, chunk in enumerate(chunks, start=1):
        metadata = chunk["metadata"]
        text = str(chunk["text"])[:MAX_CONTEXT_CHARS_PER_CHUNK]
        sections.append(
            "\n".join(
                [
                    f"[Source {index}]",
                    f"Title: {metadata.get('source_title')}",
                    f"URL: {metadata.get('source_url')}",
                    f"Chunk ID: {chunk.get('chunk_id')}",
                    f"Distance: {chunk.get('distance'):.4f}",
                    "Text:",
                    text,
                ]
            )
        )
    return "\n\n".join(sections)


def unique_sources(chunks: list[dict[str, Any]]) -> list[dict[str, str]]:
    seen = set()
    sources = []
    for chunk in chunks:
        metadata = chunk["metadata"]
        key = (metadata.get("source_title"), metadata.get("source_url"))
        if key in seen:
            continue
        seen.add(key)
        sources.append(
            {
                "title": str(metadata.get("source_title")),
                "url": str(metadata.get("source_url")),
                "chunk_id": str(chunk.get("chunk_id")),
                "distance": f"{chunk.get('distance'):.4f}",
            }
        )
    return sources


def filter_context_chunks(chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    qualified = [
        chunk
        for chunk in chunks
        if chunk["distance"] <= MAX_CONTEXT_DISTANCE
    ]
    if not qualified:
        return []

    best_distance = qualified[0]["distance"]
    return [
        chunk
        for chunk in qualified
        if chunk["distance"] <= best_distance + MAX_DISTANCE_FROM_BEST
    ][:MAX_CONTEXT_CHUNKS]


def build_user_prompt(question: str, chunks: list[dict[str, Any]]) -> str:
    return f"""Question:
{question}

Retrieved documents:
{format_context(chunks)}

Answer the question using only the retrieved documents above. If the documents do not contain the answer, say you do not have enough information. Do not add explanations that are not directly supported by the retrieved text. If multiple relevant menu items are present, include all of them instead of only the first one.
"""


def get_client() -> Groq:
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GROQ_API_KEY. Add it to .env before running generation.")
    return Groq(api_key=api_key)


def generate_answer(question: str, chunks: list[dict[str, Any]]) -> str:
    if not chunks:
        return "I don't have enough information on that."

    client = get_client()
    response = client.chat.completions.create(
        model=MODEL_NAME,
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(question, chunks)},
        ],
    )
    return response.choices[0].message.content.strip()


def ask(question: str, top_k: int = DEFAULT_TOP_K) -> dict[str, Any]:
    question = question.strip()
    if not question:
        return {"answer": "Please enter a question.", "sources": [], "chunks": []}

    retrieved_chunks = retrieve(question, top_k=top_k)
    context_chunks = filter_context_chunks(retrieved_chunks)
    answer = generate_answer(question, context_chunks)
    sources = unique_sources(context_chunks)
    return {"answer": answer, "sources": sources, "chunks": retrieved_chunks}


def print_answer(result: dict[str, Any]) -> None:
    print("\nAnswer")
    print("=" * 80)
    print(result["answer"])
    print("\nSources")
    print("=" * 80)
    for source in result["sources"]:
        print(
            f"- {source['title']} ({source['url']}) "
            f"chunk={source['chunk_id']} distance={source['distance']}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Ask a grounded question against the dining RAG system.")
    parser.add_argument("question", help="Question to ask.")
    parser.add_argument("--top-k", type=int, default=DEFAULT_TOP_K)
    args = parser.parse_args()
    print_answer(ask(args.question, top_k=args.top_k))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
