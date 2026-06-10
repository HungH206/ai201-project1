"""Gradio interface for the UH dining RAG system."""

from __future__ import annotations

import os

import gradio as gr

from query import ask


def handle_query(question: str) -> tuple[str, str]:
    try:
        result = ask(question)
    except Exception as exc:
        return f"Error: {exc}", ""

    sources = "\n".join(
        f"- {source['title']} | {source['url']} | {source['chunk_id']} | distance {source['distance']}"
        for source in result["sources"]
    )
    return result["answer"], sources


with gr.Blocks(title="UH Dining Guide") as demo:
    gr.Markdown("# UH Dining Guide")
    gr.Markdown("Ask a question about the collected UH dining, menu, meal plan, and outage documents.")

    question = gr.Textbox(
        label="Your question",
        placeholder="Example: Is there a commuter meal plan?",
        lines=2,
    )
    ask_button = gr.Button("Ask", variant="primary")
    answer = gr.Textbox(label="Answer", lines=8)
    sources = gr.Textbox(label="Retrieved from", lines=6)

    ask_button.click(handle_query, inputs=question, outputs=[answer, sources])
    question.submit(handle_query, inputs=question, outputs=[answer, sources])


if __name__ == "__main__":
    port = int(os.getenv("GRADIO_SERVER_PORT", "8061"))
    demo.launch(server_port=port)
