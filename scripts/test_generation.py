#!/usr/bin/env python3
"""Run grounded generation smoke tests."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from query import ask


TEST_QUERIES = [
    "Does The Burger Joint have any alcoholic root beer?",
    "Is there a commuter meal plan?",
    "What parking permit should I buy for UH?",
]


def main() -> int:
    for question in TEST_QUERIES:
        result = ask(question)
        print("\n" + "=" * 100)
        print(f"Question: {question}")
        print("=" * 100)
        print(result["answer"])
        print("\nSources:")
        if result["sources"]:
            for source in result["sources"]:
                print(
                    f"- {source['title']} | {source['url']} | "
                    f"{source['chunk_id']} | distance {source['distance']}"
                )
        else:
            print("- None")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
