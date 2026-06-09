# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->
My domain would be trying out the campus dining mock at the University of Houston. We have some information in relation to the Dining website on campus and menu from our local restaurant. We also add information of the latest hours at the university, the meal plan information, and the Dietary, Allergen Restrictions. It could be hard to update the time or what kind of places open in the summer, but let's say the Student Center is the only location open and any other dining halls are closed due to renovation in the Hall, then it's hard to incorporate constant change from these location to the University App System to get student on the latest news of dining changes.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or destination |
|---|--------|-------------|--------------------|
| 1 | Website  | Chick-fil-A Menu | https://dineoncampus.com/uh/whats-on-the-menu/chick-fil-a/2026-06-08/every-day|
| 2 | Website  | Panda Express Menu | https://dineoncampus.com/uh/whats-on-the-menu/panda-express/2026-06-08/every-day|
| 3 | Website | The Taco Stand Menu | https://tacostandhtx.com/lunch-dinner/ |
| 4 | Website | The Burger Joint Menu | https://burgerjointhtx.com/restaurant-menu/|
| 5 | Website | Starbucks Menu | https://www.starbucks.com/menu/|
| 6 | Website | McAlister's Deli Menu | https://www.mcalistersdeli.com/menu/| |
| 7 | Website | RAD Center Reddit Review | https://www.reddit.com/r/UniversityOfHouston/comments/1f3sgas/food_at_rad_center/|
| 8 | Website | Time Table at UH | https://dineoncampus.com/uh/hours-of-operation|
| 9 | Website | Meal Plan Information | https://dineoncampus.com/uh/20262027-meal-plans|
| 10 | Website | Dietary & Allergen Restrictions | https://new.dineoncampus.com/uh/dietary-and-allergen-restrictions|

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->
Since these sources are taken in the form of a website, Recursive Chunking is best fit. 

**Chunk size:** 500 tokens

**Overlap:** 75 tokens

**Reasoning:** I will use recursive chunking because the documents are mostly structured webpages with headings, menus, hours, meal plan sections, and allergen information. Recursive chunking helps preserve natural sections instead of cutting text randomly. A 500-token chunk is large enough to keep related dining information together, while a 75-token overlap helps maintain context when details continue between sections. For menu and hours pages, chunks will be organized around restaurant names, menu categories, locations, and date/time sections.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** sentence-transformers (all-MiniLM-L6-v2)

**Top-k:** 5 chunks per Query

**Production tradeoff reflection:** I am using `all-MiniLM-L6-v2` because it is lightweight, fast, free to run locally, and works well for a first RAG app. Since my domain is campus dining information, most questions will ask about a specific restaurant, menu item, dining location, meal plan, hours, or allergen restriction. Retrieving the top 5 chunks gives the model enough context without overwhelming it with too much unrelated information.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|-------------------------------------------|-----------------|
| 1 | What is the current hours at Chick-Fil-A? | The current opening hours are from 8am to 4pm, Monday to Thursday|
| 2 | What are the spicy items available at Panda Express? | Kung Pao Chicken, Beijing Beef, Spicy Orange Chicken, Sweetfire Chicken Breast, Black Pepper Steak, Black Pepper Chicken|
| 3 | Is The Burger Joint open on campus this summer? | No |
| 4 | Is Shellfish a common food allergen? | Yes |
| 5 | Is the meal plan only for student with on-campus residential status?| No, the meal plans are for both student with on-campus residential status and commuter status. |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. The AI model could not get the right information of the Student Review and the time opening of all food court locations.

2. It could only reference limited information provided in the website while not telling the full

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
