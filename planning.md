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
| 1 | Website  | Chick-fil-A Menu | https://chick-fil-a-menu.net |
| 2 | Website  | Panda Express Menu | https://pandaexpressmenuu.us |
| 3 | Website | The Taco Stand Lunch and Dinner Menu | https://tacostandhtx.com/lunch-dinner/ |
| 4 | Website | The Burger Joint Menu | https://burgerjointhtx.com/restaurant-menu/|
| 5 | Website | Starbucks Menu | https://starbucksreserveonly.com |
| 6 | Website | What It Do BBQ Menu | https://www.whatitdobbq.com/menu |
| 7 | Website | Food At University of Houston | https://thedailycougar.com/2023/07/15/food-on-campus-a-look-at-what-uh-has-to-offer/ |
| 8 | Website | University of Houston Hours of Operation | https://www.uh.edu/studentcenters/about-us/hours-of-operation/index.php |
| 9 | Website | University of Houston Meal Plan Information | https://www.uh.edu/af-auxiliary-services/dining-services/meal-plan-rates/meal-plan-rates.php |
| 10 | Website | University of Houston Dining Outage Tracker | https://www.uh.edu/af-auxiliary-services/dining-services/dining-outage-tracker/ |
| 11 | Local text | Panda Express Entree Reference | documents/manual/11_manual_panda_entrees.txt |
| 12 | Local text | University of Houston Dining Halls Reference | documents/manual/12_manual_uh_dining_halls.txt |
| 13 | Local text | University of Houston Meal Plan Eligibility Reference | documents/manual/13_manual_meal_plan_eligibility.txt |

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
| 1 | What are the breakfast items at Chick-fil-A? | Chick-fil-A breakfast items include Chicken Biscuit, Spicy Chicken Biscuit, Chick-n-Minis, Egg White Grill, Hash Brown Scramble Burrito, Hash Brown Scramble Bowl, Chicken, Egg & Cheese Biscuit, Bacon, Egg & Cheese Biscuit, Sausage, Egg & Cheese Biscuit, breakfast muffins, Hash Browns, Berry Parfait, and Fruit Cup. |
| 2 | What entree items are available at Panda Express? | Panda Express entree items include options such as Orange Chicken, Kung Pao Chicken, Beijing Beef, Black Pepper Chicken, Honey Sesame Chicken Breast, Grilled Teriyaki Chicken, Broccoli Beef, Mushroom Chicken, String Bean Chicken Breast, Honey Walnut Shrimp, and Black Pepper Angus Steak. |
| 3 | Does The Burger Joint have any alcoholic root beer? | Yes. The Burger Joint menu lists Not Your Father's Root Beer Float as alcoholic and also lists St. Arnold's Root Beer Float. |
| 4 | Are there any dining halls at the University of Houston? | Yes. The UH food source mentions dining halls such as Moody Towers Dining Commons and Cougar Woods Dining Commons. |
| 5 | Is there a commuter meal plan? | Yes. The meal plan source lists Block and Cougar Dining Dollars plans, and it mentions commuter students in the meal plan eligibility/cancellation information. |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. The AI model could get the right food information, but will miss some items categories.

2. It could only reference limited information provided in the website while not telling the full context of temporary closures, renovations, or special summer schedules. 

3. Menu information may change often, so the system could give outdated answers if the documents are not refreshed regularly. This is especially important for daily menus, limited-time items, and restaurant hours.

4. Student articles about UH Dining may be opinion-based, so the system needs to separate factual information from personal opinions.
---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

```mermaid
flowchart LR
    A[Document Ingestion<br>Web scraping / manual URLs] --> B[Chunking<br>Recursive text splitter<br>500 tokens, 75 overlap]
    B --> C[Embedding + Vector Store<br>all-MiniLM-L6-v2<br>FAISS or Chroma]
    C --> D[Retrieval<br>Top-k = 5 chunks]
    D --> E[Generation<br>LLM answer with source context]
    E --> F[User Interface<br>Simple chatbot or CLI app]

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

I will use ChatGPT or Claude to help create the document ingestion and chunking code. I will provide the AI tool with my Documents section, Chunking Strategy section, and the list of URLs. I expect it to produce code that loads webpage text, cleans unnecessary navigation content, and splits the text into 500-token chunks with 75-token overlap. I will verify the output by printing sample chunks and checking that menu items, hours, and allergen information are not split in confusing ways.


**Milestone 4 — Embedding and retrieval:**

I will use Claude Code to help implement embeddings and vector search. I will give it my Retrieval Approach section and ask it to use `sentence-transformers` with `all-MiniLM-L6-v2`. I expect it to produce code that embeds each chunk, stores the vectors in a local vector database such as FAISS or Chroma, and retrieves the top 5 most relevant chunks for a user question. I will verify this by testing my five evaluation questions and checking whether the retrieved chunks contain the correct source information.


**Milestone 5 — Generation and interface:**

I will use Claude Code to help build the final question-answering interface. I will provide the full planning document, especially the Evaluation Plan and Retrieval Approach. I expect it to produce a simple chatbot or command-line interface that takes a user question, retrieves relevant chunks, and generates an answer using only the retrieved context. I will verify the output by asking the five test questions and comparing the answers to the expected answers in my Evaluation Plan.
