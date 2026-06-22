import httpx
import logging
from config import config

logger = logging.getLogger(__name__)

GOVT_SITE_PRIORITY = [
    "myscheme.gov.in",
    "pmindia.gov.in",
    "india.gov.in",
    "jansuraksha.gov.in",
    "pmkisan.gov.in",
    "scholarships.gov.in",
    "mkisan.gov.in",
]

def build_search_query(user_query: str) -> str:
    """Add government site focus to search query"""
    return f"{user_query} Indian government scheme site:gov.in OR site:myscheme.gov.in"

def search_web(query: str) -> list[dict]:
    """Search using Serper API and return results"""
    if not config.SERPER_API_KEY:
        logger.warning("SERPER_API_KEY not set — skipping web search")
        return []

    try:
        with httpx.Client(timeout=8.0) as client:
            response = client.post(
                "https://google.serper.dev/search",
                headers={
                    "X-API-KEY": config.SERPER_API_KEY,
                    "Content-Type": "application/json"
                },
                json={
                    "q": build_search_query(query),
                    "num": config.MAX_SEARCH_RESULTS,
                    "gl": "in",   # India
                    "hl": "en",   # English
                }
            )
            response.raise_for_status()
            data = response.json()

            results = []

            # Extract organic results
            for item in data.get("organic", [])[:config.MAX_SEARCH_RESULTS]:
                results.append({
                    "title": item.get("title", ""),
                    "snippet": item.get("snippet", ""),
                    "link": item.get("link", ""),
                    "source": item.get("displayLink", "")
                })

            # Extract answer box if present (direct answer from Google)
            if "answerBox" in data:
                box = data["answerBox"]
                results.insert(0, {
                    "title": box.get("title", "Featured Answer"),
                    "snippet": box.get("answer") or box.get("snippet", ""),
                    "link": box.get("link", ""),
                    "source": "Google Featured Snippet"
                })

            logger.info(f"Web search returned {len(results)} results for: {query[:50]}")
            return results

    except httpx.TimeoutException:
        logger.warning("Web search timed out")
        return []
    except Exception as e:
        logger.error(f"Web search error: {e}")
        return []

def format_search_results(results: list[dict]) -> str:
    """Format search results into context string for LLM — kept short to save tokens"""
    if not results:
        return ""

    lines = ["[LIVE WEB SEARCH RESULTS]\n"]
    for i, r in enumerate(results, 1):
        # Truncate snippet to 150 chars to save tokens
        snippet = r['snippet'][:150] + "..." if len(r['snippet']) > 150 else r['snippet']
        lines.append(f"{i}. {r['title']}")
        lines.append(f"   {snippet}")
        if r['link']:
            lines.append(f"   Source: {r['link']}")
        lines.append("")

    return "\n".join(lines)

def should_search_web(confidence: float, query: str = "", schemes_found: list = []) -> bool:
    """Trigger web search for named schemes not in dataset"""

    scheme_keywords = [
        "yojana", "scheme", "mission", "abhiyan", "portal",
        "program", "programme", "initiative", "board", "samman",
        "nidhi", "bima", "viksit", "pradhan", "mukhya", "rashtriya"
    ]

    query_lower = query.lower()
    has_scheme_keyword = any(kw in query_lower for kw in scheme_keywords)

    if has_scheme_keyword:
        # Check word overlap with retrieved schemes
        query_words = set(query_lower.split())
        for scheme in schemes_found:
            scheme_name = scheme.get("name", "").lower()
            scheme_words = set(scheme_name.split())
            overlap = len(query_words & scheme_words) / max(len(query_words), 1)
            if overlap >= 0.5:
                return False  # Good match in dataset
        # Named scheme but no strong match — search web
        return True

    # For general queries, use confidence threshold
    # Your RAG returns raw scores — empirically low is below 16
    if confidence < 16.0:
        return True

    return False