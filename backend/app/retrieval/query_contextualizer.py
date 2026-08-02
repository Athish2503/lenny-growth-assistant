import re
from typing import Any, List, Optional

STOPWORDS = {
    "who", "what", "where", "when", "why", "how", "is", "are", "was", "were",
    "the", "a", "an", "this", "that", "these", "those", "in", "on", "at", "to",
    "for", "with", "from", "by", "of", "and", "or", "not", "no", "yes", "can",
    "could", "would", "should", "do", "does", "did", "tell", "me", "about",
    "give", "summarize", "explain", "describe", "show", "detail", "details",
    "advice", "think", "opinion", "framework", "strategy", "podcast", "lenny",
    "guest", "user", "assistant", "system", "please", "thanks", "thank", "you",
    "he", "his", "him", "she", "her", "hers", "they", "them", "their", "theirs", "it", "its"
}

RELATIVE_TRIGGERS = [
    "he", "his", "him", "she", "her", "hers", "they", "them", "their", "theirs",
    "it", "its", "this", "that", "these", "those", "same", "such",
    "what else", "tell me more", "summarize", "explain more", "more details",
    "give examples", "expand", "elaborate", "how about", "what about"
]


from app.retrieval.spelling_corrector import spelling_corrector


def contextualize_query(query: str, history: Optional[List[Any]] = None) -> str:
    """
    Contextualizes a user query using conversation history to resolve pronouns
    and relative references (anaphora resolution) for hybrid retrieval.
    Includes automatic fuzzy spelling correction for guest names and query typos.
    """
    if not query or not query.strip():
        return ""

    # First, run fuzzy spelling correction and guest entity normalization
    corrected_query, _ = spelling_corrector.correct_query(query)
    working_query = corrected_query.strip()

    if not history:
        return working_query

    query_lower = working_query.lower()

    # Check if query contains relative triggers (pronouns or follow-up phrases)
    has_relative = any(
        re.search(r'\b' + re.escape(trigger) + r'\b', query_lower)
        for trigger in RELATIVE_TRIGGERS
    )

    # If query is long (>= 6 words) and has no relative pronouns, it's already self-contained
    if not has_relative and len(query.split()) >= 6:
        return query.strip()

    subjects: List[str] = []

    # 1. First search user messages in history backwards for non-stopword entity terms
    for msg in reversed(history):
        role = getattr(msg, "role", None) or (msg.get("role") if isinstance(msg, dict) else "user")
        if role != "user":
            continue

        content = getattr(msg, "content", None) or (msg.get("content") if isinstance(msg, dict) else str(msg))
        if not content:
            continue

        # Extract non-stopword terms from user message
        words = [w.strip('.,!?"\'()[]:;') for w in content.split()]
        filtered_words = [w for w in words if w.lower() not in STOPWORDS and len(w) > 1]

        if filtered_words:
            candidate = " ".join(filtered_words)
            if candidate not in subjects and candidate.lower() not in query_lower:
                subjects.append(candidate)
                break  # Primary entity found from user query history!

    # 2. Search message metadata / citations if available
    if not subjects:
        for msg in reversed(history):
            metadata = getattr(msg, "metadata_json", None) or (msg.get("metadata") if isinstance(msg, dict) else {})
            if isinstance(metadata, dict):
                citations = metadata.get("citations") or metadata.get("sources") or []
                for c in citations:
                    guest = c.get("guest") or c.get("metadata", {}).get("guest")
                    if guest and guest.lower() not in STOPWORDS and guest.lower() not in query_lower:
                        subjects.append(guest)
                        break
            if subjects:
                break

    # 3. Fallback: Search capitalized proper nouns from assistant/user content
    if not subjects:
        for msg in reversed(history[-4:]):
            content = getattr(msg, "content", None) or (msg.get("content") if isinstance(msg, dict) else str(msg))
            if not content:
                continue

            words = content.split()
            for i in range(len(words)):
                w = words[i].strip('.,!?"\'()[]:;')
                if w and w[0].isupper() and w.lower() not in STOPWORDS:
                    if i + 1 < len(words):
                        w2 = words[i + 1].strip('.,!?"\'()[]:;')
                        if w2 and w2[0].isupper() and w2.lower() not in STOPWORDS:
                            candidate = f"{w} {w2}"
                            if candidate not in subjects and candidate.lower() not in query_lower:
                                subjects.append(candidate)

    if subjects:
        missing_subjects = [s for s in subjects if s.lower() not in query_lower]
        if missing_subjects:
            prefix = " ".join(missing_subjects[:2])
            return f"{prefix} {query.strip()}"

    return query.strip()
