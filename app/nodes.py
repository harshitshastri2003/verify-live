import os
from langchain_groq import ChatGroq
from tavily import TavilyClient
from app.models import ExtractedClaims, Verdict, SufficiencyCheck, Evidence
from app.state import FactCheckState

EXTRACT_PROMPT = """You are a fact-checking assistant. Given a piece of text, extract the \
individual, atomic, checkable factual claims it contains.

Rules:
- Only extract claims that can be verified against external evidence (statistics, events, \
quotes, dates, named entities, historical facts).
- Ignore opinions, predictions, and rhetorical statements.
- Break compound sentences into separate atomic claims.
- If there are no checkable claims, return an empty list.

Text:
{text}
"""

SUFFICIENCY_PROMPT = """You are judging whether the following search results contain enough \
evidence to verify or refute this claim: "{claim}"

Search results:
{results}

If the results directly address the claim (confirm, deny, or give specific relevant facts), \
they are sufficient. If they are only generally related but don't address the specific claim, \
they are NOT sufficient — in that case, write a more targeted search query.
"""

VERDICT_PROMPT = """You are weighing evidence against a claim to reach a verdict.

Claim: "{claim}"

Evidence:
{evidence}

Based ONLY on the evidence above (not your own prior knowledge), decide:
- "Supported" if the evidence confirms the claim
- "Refuted" if the evidence contradicts the claim
- "Insufficient Evidence" if the evidence doesn't clearly confirm or deny it

You MUST cite the specific source URLs from the evidence above that back your verdict. \
If you cannot point to specific URLs supporting your label, use "Insufficient Evidence" instead.
"""


def _get_structured_llm(schema):
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
    return llm.with_structured_output(schema)


def _run_search(query: str):
    client = TavilyClient()
    response = client.search(query, max_results=5)
    return response["results"]


def extract_claims(state: FactCheckState) -> FactCheckState:
    structured_llm = _get_structured_llm(ExtractedClaims)
    prompt = EXTRACT_PROMPT.format(text=state["input_text"])
    result: ExtractedClaims = structured_llm.invoke(prompt)
    return {**state, "claims": result.claims}


def search_evidence(state: FactCheckState) -> FactCheckState:
    if not state["claims"]:
        return {**state, "evidence": [], "search_iterations": 0}

    claim = state["claims"][0]
    iterations = 0

    results = _run_search(claim.text)
    iterations += 1

    checker = _get_structured_llm(SufficiencyCheck)
    check_prompt = SUFFICIENCY_PROMPT.format(claim=claim.text, results=results)
    check: SufficiencyCheck = checker.invoke(check_prompt)

    if not check.is_sufficient and check.refined_query:
        results = _run_search(check.refined_query)
        iterations += 1

    evidence = [
        Evidence(source_url=r["url"], snippet=r["content"], supports_claim=True)
        for r in results
    ]

    return {**state, "evidence": evidence, "search_iterations": iterations}


def verdict_node(state: FactCheckState) -> FactCheckState:
    if not state["claims"]:
        return {**state, "verdicts": []}

    claim = state["claims"][0]

    if not state["evidence"]:
        verdict = Verdict(
            claim=claim.text,
            label="Insufficient Evidence",
            confidence="Low",
            reasoning="No evidence was gathered for this claim.",
            citations=[],
        )
        return {**state, "verdicts": [verdict]}

    evidence_text = "\n".join(
        f"- URL: {e.source_url}\n  Content: {e.snippet}" for e in state["evidence"]
    )

    verdict_llm = _get_structured_llm(Verdict)
    prompt = VERDICT_PROMPT.format(claim=claim.text, evidence=evidence_text)
    verdict: Verdict = verdict_llm.invoke(prompt)

    # Hard safety check: never allow Supported/Refuted without citations,
    # regardless of what the LLM decided.
    if verdict.label != "Insufficient Evidence" and not verdict.citations:
        verdict = Verdict(
            claim=claim.text,
            label="Insufficient Evidence",
            confidence="Low",
            reasoning="Model did not provide citations, so verdict was downgraded.",
            citations=[],
        )

    return {**state, "verdicts": [verdict]}