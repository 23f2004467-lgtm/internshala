"""Phase 2: 5-node LangGraph (decide → search → draft → critique → finalize)
with conditional revision loop and structured JSON output."""
from typing import TypedDict, Literal
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from .personas import get_persona
from .llm import structured_call, get_llm
from .tools import mock_searxng_search

# ----- State -----
class ContentState(TypedDict, total=False):
    bot_id: str
    persona_desc: str
    topic: str
    search_query: str
    search_results: str
    draft: str
    critique_score: float
    critique_feedback: str
    revisions: int
    final: dict

# ----- Pydantic schemas for structured outputs -----
class TopicChoice(BaseModel):
    topic: str = Field(description="A short topic the bot wants to post about today")
    search_query: str = Field(description="A 3-6 word web search query")

class Critique(BaseModel):
    score: float = Field(ge=0, le=1, description="0=off-persona, 1=perfectly in character + opinionated")
    feedback: str = Field(description="One sentence: what to improve. Empty string if score >= 0.8.")

class FinalPost(BaseModel):
    bot_id: str
    topic: str
    post_content: str

# ----- Nodes -----
# List must match keys in grid07/tools.py::_FAKE_NEWS
AVAILABLE_TOPICS = ["crypto", "ai", "regulation", "elon", "billionaire", "climate", "markets", "labor"]

def decide_search(state: ContentState) -> ContentState:
    prompt = f"""You are this bot:
{state['persona_desc']}

Available news topic keywords today: {', '.join(AVAILABLE_TOPICS)}

Pick exactly ONE keyword from the list above that your persona would have the
strongest, most opinionated take on. Then form a short search query (3-6 words)
that contains that keyword.

Return JSON with the chosen topic and the search query.
"""
    out = structured_call(prompt, TopicChoice, temperature=0.8)
    return {"topic": out.topic, "search_query": out.search_query}

def web_search(state: ContentState) -> ContentState:
    results = mock_searxng_search.invoke({"query": state["search_query"]})
    return {"search_results": results}

def draft_post(state: ContentState) -> ContentState:
    revision_note = ""
    if state.get("revisions", 0) > 0 and state.get("critique_feedback"):
        revision_note = f"\n\nPrevious draft was weak. Critic said: {state['critique_feedback']}\nFix it. Be sharper, more in character."
    prompt = f"""You are this bot:
{state['persona_desc']}

Topic: {state['topic']}
Recent news context:
{state['search_results']}

Write a single highly-opinionated post, MAX 280 characters. Take a clear stance. Use the persona's voice.
Do NOT use hashtags. Do NOT prefix with "As a [persona]". Just speak.
{revision_note}

Return ONLY the post text, nothing else.
"""
    llm = get_llm(temperature=0.9)
    raw = llm.invoke(prompt).content.strip().strip('"')
    # Hard truncate as a safety net
    if len(raw) > 280:
        raw = raw[:277].rstrip() + "..."
    return {"draft": raw, "revisions": state.get("revisions", 0) + 1}

def critique(state: ContentState) -> ContentState:
    prompt = f"""You are a strict editor checking whether this post is in character.

PERSONA:
{state['persona_desc']}

POST DRAFT:
{state['draft']}

Score 0 to 1:
- 1.0 = clearly in voice, takes a strong opinionated stance, under 280 chars.
- 0.5 = generic, hedged, or could be from any account.
- 0.0 = completely off-persona.

Return JSON {{"score": float, "feedback": str}}. If score >= 0.8 set feedback="".
"""
    out = structured_call(prompt, Critique, temperature=0.2)
    return {"critique_score": out.score, "critique_feedback": out.feedback}

def finalize(state: ContentState) -> ContentState:
    return {"final": {
        "bot_id": state["bot_id"],
        "topic": state["topic"],
        "post_content": state["draft"],
    }}

def should_revise(state: ContentState) -> Literal["draft_post", "finalize"]:
    if state["critique_score"] >= 0.7 or state["revisions"] >= 2:
        return "finalize"
    return "draft_post"

# ----- Graph assembly -----
def build_graph():
    g = StateGraph(ContentState)
    g.add_node("decide_search", decide_search)
    g.add_node("web_search", web_search)
    g.add_node("draft_post", draft_post)
    g.add_node("critique", critique)
    g.add_node("finalize", finalize)

    g.set_entry_point("decide_search")
    g.add_edge("decide_search", "web_search")
    g.add_edge("web_search", "draft_post")
    g.add_edge("draft_post", "critique")
    g.add_conditional_edges("critique", should_revise, {
        "draft_post": "draft_post",
        "finalize": "finalize",
    })
    g.add_edge("finalize", END)
    return g.compile()

def generate_post(bot_id: str) -> dict:
    p = get_persona(bot_id)
    graph = build_graph()
    out = graph.invoke({"bot_id": bot_id, "persona_desc": p.description, "revisions": 0})
    return out["final"]
