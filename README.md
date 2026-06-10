# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->

---

My domain would be trying out the campus dining mock at the University of Houston. We have some information in relation to the Dining website on campus and menu from our local restaurant. We also add information of the latest hours at the university, the meal plan information, and the Dietary, Allergen Restrictions.



## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Chick-fil-A Menu | Website | https://chick-fil-a-menu.net |
| 2 | Panda Express Menu | Website | https://pandaexpressmenuu.us |
| 3 | The Taco Stand Lunch and Dinner Menu | Website | https://tacostandhtx.com/lunch-dinner/ |
| 4 | The Burger Joint Menu | Website | https://burgerjointhtx.com/restaurant-menu/ |
| 5 | Starbucks Menu | Website | https://starbucksreserveonly.com |
| 6 | What It Do BBQ Menu | Website | https://www.whatitdobbq.com/menu |
| 7 | Food At University of Houston | Website | https://thedailycougar.com/2023/07/15/food-on-campus-a-look-at-what-uh-has-to-offer/ |
| 8 | University of Houston Hours of Operation | Website | https://www.uh.edu/studentcenters/about-us/hours-of-operation/index.php |
| 9 | University of Houston Meal Plan Information | Website | https://www.uh.edu/af-auxiliary-services/dining-services/meal-plan-rates/meal-plan-rates.php |
| 10 | University of Houston Dining Outage Tracker | Website | https://www.uh.edu/af-auxiliary-services/dining-services/dining-outage-tracker/ |
| 11 | Panda Express Entree Reference | Local text | documents/manual/11_manual_panda_entrees.txt |
| 12 | University of Houston Dining Halls Reference | Local text | documents/manual/12_manual_uh_dining_halls.txt |
| 13 | University of Houston Meal Plan Eligibility Reference | Local text | documents/manual/13_manual_meal_plan_eligibility.txt |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** 500 tokens

**Overlap:** 75 tokens

**Why these choices fit your documents:** Most sources are restaurant menus, UH dining pages, and short local reference notes. A 500-token chunk keeps related menu sections, meal plan details, and dining hall context together, while a 75-token overlap helps preserve context when an item list or policy explanation crosses a chunk boundary. The pipeline strips HTML, cookie text, repeated navigation, and footers where possible, and it uses local text references for facts that were buried or missing in noisy web pages.


**Final chunk count:**
Final Chunk Count: 56 chunks

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:** `sentence-transformers/all-MiniLM-L6-v2`

**Production tradeoff reflection:** I used `all-MiniLM-L6-v2` because it runs locally with no API key, has low latency, and is strong enough for a small RAG corpus. If this were deployed for real users and cost was not a constraint, I would compare larger embedding models for better semantic accuracy, longer context handling, and stronger performance on noisy menu/policy text. I would also weigh latency and whether the model should run locally or through a hosted API.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:** The generation code uses this system instruction in `query.py`: "Answer using only the provided retrieved documents. Do not use outside knowledge, assumptions, or guesses. Do not explain using brand knowledge, common knowledge, or facts that are not directly stated in the retrieved text. If the retrieved documents do not contain enough information, answer exactly: 'I don't have enough information on that.' Keep the answer concise and factual. Do not invent source names or URLs."

The `ask()` function also filters retrieval results before generation. Only chunks with distance `<= 0.65` are included in the LLM context, and at most three chunks are passed to the model. If no retrieved chunk passes that threshold, the system returns "I don't have enough information on that" without calling the LLM.

**How source attribution is surfaced in the response:** Source attribution is appended programmatically instead of relying on the LLM to cite sources. The Gradio interface displays a separate "Retrieved from" field containing each source title, source URL or local file path, chunk id, and distance score.

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What are the breakfast items at Chick-fil-A? | Chick-fil-A breakfast items include Chicken Biscuit, Spicy Chicken Biscuit, Chick-n-Minis, Egg White Grill, Hash Brown Scramble Burrito, Hash Brown Scramble Bowl, Chicken, Egg & Cheese Biscuit, Bacon, Egg & Cheese Biscuit, Sausage, Egg & Cheese Biscuit, breakfast muffins, Hash Browns, Berry Parfait, and Fruit Cup. | Retrieved Chick-fil-A chunks first, including the breakfast menu and breakfast item list. | Relevant | Accurate |
| 2 | What entree items are available at Panda Express? | Panda Express entree items include options such as Orange Chicken, Kung Pao Chicken, Beijing Beef, Black Pepper Chicken, Honey Sesame Chicken Breast, Grilled Teriyaki Chicken, Broccoli Beef, Mushroom Chicken, String Bean Chicken Breast, Honey Walnut Shrimp, and Black Pepper Angus Steak. | Retrieved the local Panda Express entree reference as the top result, followed by Panda Express menu chunks. | Relevant | Accurate |
| 3 | Does The Burger Joint have any alcoholic root beer? | Yes. The Burger Joint menu lists Not Your Father's Root Beer Float as alcoholic and also lists St. Arnold's Root Beer Float. | Retrieved The Burger Joint menu first with Not Your Father's Root Beer Float marked as alcoholic. | Relevant | Accurate |
| 4 | Are there any dining halls at the University of Houston? | Yes. The UH food source mentions dining halls such as Moody Towers Dining Commons and Cougar Woods Dining Commons. | Retrieved the local UH dining halls reference first, including Moody Towers Dining Commons and Cougar Woods Dining Commons. | Relevant | Accurate |
| 5 | Is there a commuter meal plan? | Yes. The meal plan source lists Block and Cougar Dining Dollars plans, and it mentions commuter students in the meal plan eligibility/cancellation information. | Retrieved the local UH meal plan eligibility reference first, including commuter students and Block/Cougar Dining Dollars plans. | Relevant | Accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**

**What the system returned:**

**Root cause (tied to a specific pipeline stage):**

**What you would change to fix it:**

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**

**One way your implementation diverged from the spec, and why:**

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*

**Instance 2**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*
