# Verify Live

Agentic fact-checking tool. Takes a claim, extracts the checkable parts, searches the web for evidence, and returns a grounded verdict — never a verdict without citations.

**Live:** [https://verify-live.onrender.com](https://verify-live.onrender.com)

## Architecture

Built as a LangGraph pipeline with three nodes:



START → extract_claims → search_evidence → verdict → END



**Extracting claims.** The input text goes to Llama-3.3-70B on Groq, but instead of asking it to "output JSON" and hoping for the best, I force it through a Pydantic schema using LangChain's structured output (which uses tool calling under the hood). This also filters out opinions and predictions — if you write "I think Paris is beautiful," it correctly ignores that and only pulls out the actual factual claim.

**Searching and judging.** This is the part I actually care about — it's not just "search once and hope." After the first search, the model looks at what came back and decides for itself whether it's actually enough to verify the claim, or too vague/generic. If it's not enough, it writes its own better search query and tries again. I capped it at one retry, mostly to keep response times sane, but the point is the model is making the call, not a hardcoded loop counter.

**Reaching a verdict.** The model weighs the evidence it actually gathered — not its own training data — and picks Supported, Refuted, or Insufficient Evidence, with a confidence level and the specific URLs it's basing that on. I don't fully trust it to always cite properly though, so there's a backup check in the code itself: if it ever says Supported or Refuted without listing any citations, I override it and force it down to Insufficient Evidence. Prompts get ignored sometimes; code doesn't.

## Stack

- LangGraph for the agent loop

- Groq (Llama-3.3-70B) as the LLM, through langchain-groq

- Tavily for web search

- Pydantic schemas everywhere an LLM output needs to be trusted downstream

- FastAPI backend, one endpoint

- React frontend, kept intentionally simple — just an input box and a verdict card

- Docker (two-stage build, one for building the React app, one for actually running it), deployed on Render

## Running it yourself

```bash

pip install -r requirements.txt

cd frontend && npm install && cd ..

```

You'll need a `.env` at the root with:

GROQ_API_KEY=...  
TAVILY_API_KEY=...

Then run the backend and frontend separately:

```bash

uvicorn app.api:app --reload

cd frontend && npm run dev

```

## What it doesn't do yet

Right now it only checks the first claim it extracts — if you paste in a paragraph with three separate facts, it'll find all three but only actually verify the first one. Extending that to loop over all of them is on my list, just didn't want to add width before the core logic was solid.

 