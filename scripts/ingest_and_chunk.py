#!/usr/bin/env python3
"""Load, clean, and chunk Project 1 dining documents."""

from __future__ import annotations

import argparse
import io
import html
import json
import re
import ssl
import textwrap
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


CHUNK_SIZE_TOKENS = 500
CHUNK_OVERLAP_TOKENS = 75
MIN_CLEAN_TOKENS = 50
ALLOW_SHORT_SOURCES = {"10_dining_outage_tracker"}

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANUAL_DIR = PROJECT_ROOT / "documents" / "manual"
RAW_DIR = PROJECT_ROOT / "documents" / "raw"
RAW_BINARY_DIR = PROJECT_ROOT / "documents" / "raw_binary"
CLEANED_DIR = PROJECT_ROOT / "documents" / "cleaned"
CHUNKS_DIR = PROJECT_ROOT / "documents" / "chunks"


@dataclass(frozen=True)
class Source:
    slug: str
    title: str
    url: str


SOURCES = [
    Source(
        "01_chick_fil_a_menu",
        "Chick-fil-A Menu",
        "https://chick-fil-a-menu.net",
    ),
    Source(
        "02_panda_express_menu",
        "Panda Express Menu",
        "https://pandaexpressmenuu.us",
    ),
    Source(
        "03_taco_stand_menu",
        "The Taco Stand Lunch and Dinner Menu",
        "https://tacostandhtx.com/lunch-dinner/",
    ),
    Source(
        "04_burger_joint_menu",
        "The Burger Joint Menu",
        "https://burgerjointhtx.com/restaurant-menu/",
    ),
    Source(
        "05_starbucks_menu",
        "Starbucks Menu",
        "https://starbucksreserveonly.com",
    ),
    Source(
        "06_what_it_do_bbq_menu",
        "What It Do BBQ Menu",
        "https://www.whatitdobbq.com/menu",
    ),
    Source(
        "07_Food_At_UH",
        "Food At University of Houston",
        "https://thedailycougar.com/2023/07/15/food-on-campus-a-look-at-what-uh-has-to-offer/",
    ),
    Source(
        "08_uh_hours",
        "University of Houston Hours of Operation",
        "https://www.uh.edu/studentcenters/about-us/hours-of-operation/index.php",
    ),
    Source(
        "09_meal_plan_information",
        "University of Houston Meal Plan Information",
        "https://www.uh.edu/af-auxiliary-services/dining-services/meal-plan-rates/meal-plan-rates.php",
    ),
    Source(
        "10_dining_outage_tracker",
        "University of Houston Dining Outage Tracker",
        "https://www.uh.edu/af-auxiliary-services/dining-services/dining-outage-tracker/",
    ),
    Source(
        "11_manual_panda_entrees",
        "Panda Express Entree Reference",
        "manual://documents/manual/11_manual_panda_entrees.txt",
    ),
    Source(
        "12_manual_uh_dining_halls",
        "University of Houston Dining Halls Reference",
        "manual://documents/manual/12_manual_uh_dining_halls.txt",
    ),
    Source(
        "13_manual_meal_plan_eligibility",
        "University of Houston Meal Plan Eligibility Reference",
        "manual://documents/manual/13_manual_meal_plan_eligibility.txt",
    ),
]


MANUAL_FALLBACK_TEXT = {
    "06_what_it_do_bbq_menu": """
Main Menu
Catering
Main Menu
Appetizers
Taylor Smoked Chicken Flautas
$11.99
Smoked chicken thighs, bell peppers, mozzarella and cream cheese fried in a flour tortilla (550 CAL)
Mahagani Loaded Brisket Fries
$12.99
Crispy fries topped with homemade queso, brisket, and fresh pico de gallo(750 CAL)
Herman Loaded Brisket Nachos
$12.99
Fresh-made tortilla chips topped with queso, brisket, fresh pico, black olives, jalapeno ranch, and jalapenos(800 CAL)
Adriana Brisket Empandas
$13.99
Smoked brisket and fresh mozzarella cheese fried in an empanada shell(700 CAL)
Tacos
Smoked Jerk Chicken Taco
$4.99
Vinegar slaw and mango pico de gallo(350 CAL)
Smoked Brisket Taco
$5.99
Shredded cheese and pico de gallo(300 CAL)
Pulled Pork Taco
$4.99
Shredded cheese and pico de gallo(270 CAL)
Smoked Turkey Taco
$4.99
Shredded cheese and pico de gallo(300 CAL)
Fried Fish Taco
$4.99
Slaw, pico de gallo with H-Town candy drizzle(300 CAL)
Baked Potato
Greenwood Baked Potato
$12.99
Topped with butter, bacon, cheddar cheese, and chives- Add Smoked Brisket $16,99 (700 CAL)- Add Smoked Turkey $14,99 (600 CAL)
Sandwiches
My Cousin's Pulled Pork Sandwich
$14.99
Smoked pork topped with fresh coleslaw on a toasted brioche bun(650 CAL)
My Uncle's Sausage Sandwich
$14.99
Smoked pork sausage, BBQ sauce, pickles, and onions on a toasted brioche bun(900 CAL)
Brisket Sandwich
$16.99
Slow-smoked brisket, pickles, onions, and BBQ sauce on a toasted brioche bun(950 CAL)
Boxed Turkey Sandwich
$14.99
Slow-smoked turkey, pickles, onions, and BBQ sauce(750 CAL)
Fred's Fish Sandwich
$14.99
Slow- smoked turkey, pickles, onions, and BBQ sauce(750 CAL)
Salad
What It Do Chop
$9.99
Mixed greens, cheddar cheese, pico de gallo (450 CAL)- Add Smoked Brisket $16,99 (700 CAL)- Add Smoked Turkey $14,99 (600 CAL)- Add Smoked Chicken $14,99
Turkey Legs
Classic Smoked Turkey Leg
$16.00
(420 CAL)
Mac-N-Chz Stuffed Turkey Leg
$20.00
(720 CAL)
Dirty Rice Stuffed Turkey Leg
$22.00
Topped with Jalapeno Ranch(670 CAL)
Baskets
Fish Basket
$14.99
Two catfish fillets, seasoned and fried to perfection, served with tarter sauce(750 CAL)
Omar's Chicken Tender Basket
$10.99
Three tenders, seasoned and fried with your choice of dipping sauce(700 CAL)
Matt's Rib Basket
$15.99
Three smoked ribs(700 CAL)
Gilbert Boudain Ball Basket
$10.99
4 home-battered boudin balls served with fresh fries(700 CAL)
Vegan Optons
Jardai Vegan Smash Burger
$13.99
Two vegan patties, grilled onions, and vegan cheese, served with sweet potato fries(850 CAL)
Dessert
Furrest Funnel Cake Fries
$8.99
Classic funnel cake fries topped with powdered sugar(600 CAL)
Popajoe's Deep Fried Bread Pudding
$8.99
Homemade bread pudding deep fried topped with caramel and powdered sugar(750 CAL)
Keitho Churros
$8.99
Fresh fried churros tossed in our sugar cinnamon mixture(500 CAL)
Catering
Boxed Sandwiches
Brisket
$16.99
(400-750 CAL)
Turkey Breast
$14.99
(330-420 CAL)
Sausage
$14.99
(740-860 CAL)
Pulled Pork
$14.99
(480-620 CAL)
Proteins
Ribs
$33.00
Per slab(860-1,200 CAL PER POUND)
Whole Chicken
$17.99
Per chicken(468-780 CAL PER CHICKEN)
Sides
Coleslaw
(1,500 CAL HALF PAN/3,000 CAL FULL PAN )
Potato Salad
(2,000 CAL HALF PAN/4,000 CAL FULL PAN )
Dirty Rice
(2,500 CAL HALF PAN/5,000 CAL FULL PAN )
Mac & Cheese
(3,000 CAL HALF PAN/6,000 CAL FULL PAN )
Green Beans
(800 CAL HALF PAN/1,600 CAL FULL PAN )
French Fries
(3,650 CAL HALF PAN/7,300 CAL FULL PAN )
Baked Beans
(2,500 CAL HALF PAN/5,000 CAL FULL PAN )
""".strip()
}


class TextExtractor(HTMLParser):
    """Small HTML-to-text parser that skips common non-content elements."""

    SKIP_TAGS = {"script", "style", "noscript", "svg", "canvas", "iframe"}
    BLOCK_TAGS = {
        "address",
        "article",
        "aside",
        "blockquote",
        "br",
        "dd",
        "div",
        "dl",
        "dt",
        "figcaption",
        "footer",
        "form",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "header",
        "hr",
        "li",
        "main",
        "nav",
        "ol",
        "p",
        "pre",
        "section",
        "table",
        "td",
        "th",
        "tr",
        "ul",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._parts: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in self.SKIP_TAGS:
            self._skip_depth += 1
        if tag in self.BLOCK_TAGS:
            self._parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in self.SKIP_TAGS and self._skip_depth:
            self._skip_depth -= 1
        if tag in self.BLOCK_TAGS:
            self._parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        if data.strip():
            self._parts.append(data)

    def get_text(self) -> str:
        return "".join(self._parts)


def ensure_dirs() -> None:
    for directory in (MANUAL_DIR, RAW_DIR, RAW_BINARY_DIR, CLEANED_DIR, CHUNKS_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def fetch_url(url: str, timeout: int = 30) -> str:
    return fetch_url_bytes(url, timeout=timeout).decode("utf-8", errors="replace")


def fetch_url_bytes(url: str, timeout: int = 30) -> bytes:
    request = Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            return response.read()
    except URLError as exc:
        reason = getattr(exc, "reason", None)
        if not isinstance(reason, ssl.SSLCertVerificationError):
            raise

    ssl_context = ssl._create_unverified_context()
    with urlopen(request, timeout=timeout, context=ssl_context) as response:
        return response.read()


def extract_pdf_text(pdf_bytes: bytes) -> str:
    try:
        import pdfplumber
    except ImportError as exc:
        raise RuntimeError(
            "PDF source requires pdfplumber. Install project requirements with "
            "`venv/bin/pip install -r requirements.txt`."
        ) from exc

    pages = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            page_text = page.extract_text() or ""
            if page_text.strip():
                pages.append(f"Page {page_number}\n{page_text.strip()}")
    return "\n\n".join(pages)


def html_to_text(raw: str) -> str:
    parser = TextExtractor()
    parser.feed(raw)
    parser.close()
    text = parser.get_text()
    return html.unescape(text)


def clean_text(text: str) -> str:
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = remove_cookie_sections(text)

    boilerplate_patterns = [
        r"(?im)^skip to main content$",
        r"(?im)^open navigation$",
        r"(?im)^close navigation$",
        r"(?im)^share this.*$",
        r"(?im)^read more$",
        r"(?im)^cookie(s)? policy.*$",
        r"(?im)^accept all cookies$",
        r"(?im)^privacy policy$",
        r"(?im)^terms of use$",
        r"(?im)^all rights reserved.*$",
        r"(?im)^©.*$",
    ]
    for pattern in boilerplate_patterns:
        text = re.sub(pattern, "", text)

    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            lines.append("")
            continue
        if len(stripped) <= 2:
            continue
        lines.append(stripped)

    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def refine_cleaned_text(source: Source, text: str) -> str:
    if source.slug == "04_burger_joint_menu":
        marker = "\nRestaurant Menu\n"
        index = text.rfind(marker)
        if index != -1:
            return text[index + 1 :].strip()

    markers_by_source = {
        "01_chick_fil_a_menu": ["Chick-n-Strips™"],
        "03_taco_stand_menu": ["RESTAURANT MENU"],
        "08_uh_hours": ["Live Chat"],
        "09_meal_plan_information": ["2025 - 2026 Meal Plan Rates"],
        "10_dining_outage_tracker": ["Date\n\nLocation\n\nOutage/Impacts"],
    }
    for marker in markers_by_source.get(source.slug, []):
        index = text.find(marker)
        if index != -1:
            text = text[index:]
            break

    footer_markers_by_source = {
        "08_uh_hours": ["University of Houston\nHouston, Texas"],
        "09_meal_plan_information": ["University of Houston\nHouston, Texas"],
        "10_dining_outage_tracker": ["University of Houston\nHouston, Texas"],
    }
    for marker in footer_markers_by_source.get(source.slug, []):
        index = text.find(marker)
        if index != -1:
            text = text[:index]
            break

    return text.strip()


def remove_cookie_sections(text: str) -> str:
    section_starts = [
        "Cookie Preferences",
        "Privacy Preference Center",
        "Consent Preferences",
        "Manage Consent Preferences",
        "Toggle Strictly Necessary",
        "Strictly Necessary Cookies",
        "These cookies are needed for adding comments",
        "Google reCAPTCHA helps protect websites",
        "Statistics cookies collect information anonymously",
    ]
    earliest = None
    lower_text = text.lower()
    for marker in section_starts:
        index = lower_text.find(marker.lower())
        if index != -1 and (earliest is None or index < earliest):
            earliest = index

    if earliest is not None:
        text = text[:earliest]

    line_patterns = [
        r"(?im)^.*cookie.*duration.*$",
        r"(?im)^.*google analytics.*$",
        r"(?im)^.*recaptcha.*$",
        r"(?im)^.*used to track.*$",
        r"(?im)^.*used to identify users.*$",
    ]
    for pattern in line_patterns:
        text = re.sub(pattern, "", text)
    return text


def tokenize(text: str) -> list[str]:
    return re.findall(r"\S+", text)


def chunk_tokens(tokens: list[str], chunk_size: int, overlap: int) -> Iterable[list[str]]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be non-negative and smaller than chunk_size")

    step = chunk_size - overlap
    for start in range(0, len(tokens), step):
        chunk = tokens[start : start + chunk_size]
        if chunk:
            yield chunk
        if start + chunk_size >= len(tokens):
            break


def chunk_document(source: Source, cleaned_text: str) -> list[dict[str, object]]:
    tokens = tokenize(cleaned_text)
    chunks = []
    for index, chunk in enumerate(
        chunk_tokens(tokens, CHUNK_SIZE_TOKENS, CHUNK_OVERLAP_TOKENS), start=1
    ):
        chunks.append(
            {
                "chunk_id": f"{source.slug}_{index:03d}",
                "source_slug": source.slug,
                "source_title": source.title,
                "source_url": source.url,
                "chunk_index": index,
                "token_count": len(chunk),
                "text": " ".join(chunk),
            }
        )
    return chunks


def save_text(path: Path, text: str) -> None:
    path.write_text(text.strip() + "\n", encoding="utf-8")


def load_or_fetch_raw(source: Source, refresh: bool) -> tuple[str, str, str | None]:
    raw_path = RAW_DIR / f"{source.slug}.txt"
    if source.url.startswith("manual://"):
        manual_path = PROJECT_ROOT / source.url.removeprefix("manual://")
        if not manual_path.exists():
            raise FileNotFoundError(f"Missing manual source file: {manual_path}")
        raw_text = manual_path.read_text(encoding="utf-8")
        save_text(raw_path, raw_text)
        return raw_text, "manual_file", None

    if source.url.lower().endswith(".pdf"):
        pdf_path = RAW_BINARY_DIR / f"{source.slug}.pdf"
        if pdf_path.exists() and not refresh:
            pdf_bytes = pdf_path.read_bytes()
        else:
            pdf_bytes = fetch_url_bytes(source.url)
            pdf_path.write_bytes(pdf_bytes)
        raw_text = extract_pdf_text(pdf_bytes)
        save_text(raw_path, raw_text)
        return raw_text, "fetched", None

    if raw_path.exists() and not refresh:
        return raw_path.read_text(encoding="utf-8"), "cached", None

    try:
        raw_html = fetch_url(source.url)
    except (HTTPError, URLError, TimeoutError) as exc:
        fallback_text = MANUAL_FALLBACK_TEXT.get(source.slug)
        if fallback_text is None:
            raise
        save_text(raw_path, fallback_text)
        return fallback_text, "manual_fallback", str(exc)

    raw_text = html_to_text(raw_html)
    save_text(raw_path, raw_text)
    return raw_text, "fetched", None


def print_chunk_samples(chunks: list[dict[str, object]], sample_count: int = 5) -> None:
    if not chunks:
        print("No chunks were created.")
        return

    if len(chunks) <= sample_count:
        sample_indexes = list(range(len(chunks)))
    else:
        sample_indexes = sorted(
            {
                0,
                len(chunks) // 4,
                len(chunks) // 2,
                (len(chunks) * 3) // 4,
                len(chunks) - 1,
            }
        )

    print("\nRepresentative chunk inspection")
    print("=" * 80)
    for sample_number, chunk_index in enumerate(sample_indexes, start=1):
        chunk = chunks[chunk_index]
        print(
            f"\nSample {sample_number}: {chunk['chunk_id']} "
            f"({chunk['token_count']} tokens, {chunk['source_title']})"
        )
        print("-" * 80)
        preview = textwrap.shorten(str(chunk["text"]), width=900, placeholder=" ...")
        print(textwrap.fill(preview, width=100))


def run(refresh: bool) -> int:
    ensure_dirs()
    all_chunks: list[dict[str, object]] = []
    report: list[dict[str, object]] = []

    for source in SOURCES:
        print(f"Loading {source.title}")
        try:
            raw_text, load_status, load_error = load_or_fetch_raw(source, refresh=refresh)
        except (HTTPError, URLError, TimeoutError) as exc:
            print(f"  ERROR: could not fetch {source.url}: {exc}")
            report.append(
                {
                    "source_slug": source.slug,
                    "source_title": source.title,
                    "source_url": source.url,
                    "status": "fetch_error",
                    "error": str(exc),
                    "cleaned_token_count": 0,
                    "chunk_count": 0,
                }
            )
            continue

        cleaned = refine_cleaned_text(source, clean_text(raw_text))
        save_text(CLEANED_DIR / f"{source.slug}.txt", cleaned)
        cleaned_token_count = len(tokenize(cleaned))
        if cleaned_token_count < MIN_CLEAN_TOKENS and source.slug not in ALLOW_SHORT_SOURCES:
            print(
                f"  SKIPPED: only {cleaned_token_count} cleaned words. "
                "This looks like a placeholder or blocked page."
            )
            report.append(
                {
                    "source_slug": source.slug,
                    "source_title": source.title,
                    "source_url": source.url,
                    "status": "skipped_too_short",
                    "error": None,
                    "cleaned_token_count": cleaned_token_count,
                    "chunk_count": 0,
                }
            )
            continue

        chunks = chunk_document(source, cleaned)
        all_chunks.extend(chunks)
        load_status_message = (
            f"; loaded from {load_status}"
            + (f" after fetch error: {load_error}" if load_error else "")
        )
        print(
            f"  raw words: {len(tokenize(raw_text))}; "
            f"cleaned words: {cleaned_token_count}; chunks: {len(chunks)}"
            f"{load_status_message}"
        )
        report.append(
            {
                "source_slug": source.slug,
                "source_title": source.title,
                "source_url": source.url,
                "status": "chunked" if load_status != "manual_fallback" else "chunked_manual_fallback",
                "error": load_error,
                "cleaned_token_count": cleaned_token_count,
                "chunk_count": len(chunks),
            }
        )

    chunks_path = CHUNKS_DIR / "chunks.jsonl"
    with chunks_path.open("w", encoding="utf-8") as output:
        for chunk in all_chunks:
            output.write(json.dumps(chunk, ensure_ascii=True) + "\n")

    report_path = CHUNKS_DIR / "ingestion_report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    print(f"\nSaved {len(all_chunks)} chunks to {chunks_path.relative_to(PROJECT_ROOT)}")
    print(f"Saved ingestion report to {report_path.relative_to(PROJECT_ROOT)}")
    if len(all_chunks) < 50:
        print("WARNING: fewer than 50 chunks. Inspect whether source text is missing or chunks are too large.")
    elif len(all_chunks) > 2000:
        print("WARNING: more than 2000 chunks. Inspect whether chunks are too small.")

    print_chunk_samples(all_chunks)
    return 0 if all_chunks else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Fetch URLs again even when documents/raw/*.txt already exists.",
    )
    args = parser.parse_args()
    return run(refresh=args.refresh)


if __name__ == "__main__":
    raise SystemExit(main())
