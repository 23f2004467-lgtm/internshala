"""Mock web search keyed off keywords."""
from langchain_core.tools import tool

_FAKE_NEWS = {
    "crypto": [
        "Bitcoin hits new all-time high amid regulatory ETF approvals.",
        "Ethereum staking yields cross 8% as institutional flow surges.",
    ],
    "ai": [
        "OpenAI rumored to release GPT-5 with autonomous agent capabilities.",
        "Anthropic raises $20B in latest funding round to expand training compute.",
    ],
    "regulation": [
        "EU AI Act enforcement begins; first fines expected within 60 days.",
        "SEC announces new rules for retail crypto exchanges.",
    ],
    "elon": [
        "SpaceX Starship completes 5th orbital test flight successfully.",
        "Tesla announces Robotaxi rollout to 12 new cities this quarter.",
    ],
    "billionaire": [
        "Top 10 billionaires now hold more wealth than the bottom 50% globally.",
        "Tech founders pour $4B into longevity research startups.",
    ],
    "climate": [
        "Renewable capacity additions outpaced fossil fuels for the third year.",
        "Major insurers exit coastal markets citing climate risk.",
    ],
    "markets": [
        "S&P 500 posts third consecutive weekly gain as inflation cools.",
        "10-year Treasury yield drops to 3.8% on rate-cut expectations.",
    ],
    "labor": [
        "Tech sector layoffs cross 200,000 year-to-date amid AI restructuring.",
        "Strike wave hits logistics; retailers brace for holiday disruption.",
    ],
}

@tool
def mock_searxng_search(query: str) -> str:
    """Returns recent news headlines based on keywords in the query."""
    q = query.lower()
    hits: list[str] = []
    for keyword, items in _FAKE_NEWS.items():
        if keyword in q:
            hits.extend(items)
    if not hits:
        hits = ["No specific news; markets stable, tech sector mixed, geopolitics tense."]
    return "\n".join(f"- {h}" for h in hits[:4])
