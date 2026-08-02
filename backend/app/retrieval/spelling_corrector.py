import json
import re
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


class SpellingCorrector:
    """
    Fuzzy spelling corrector and entity normalizer for Lenny Growth Assistant.
    Auto-detects misspelled guest names, companies, and product terms using difflib
    and normalizes them to canonical entity names in the podcast corpus.
    """

    def __init__(self, corpus_path: Optional[Path] = None):
        self.known_guests: Set[str] = set()
        self.known_guest_list: List[str] = []
        self.guest_words: Set[str] = set()
        self._load_corpus_entities(corpus_path)

    def _load_corpus_entities(self, corpus_path: Optional[Path] = None) -> None:
        """
        Loads guest names and topics from data/processed/chunks.json.
        """
        paths_to_try = [
            corpus_path,
            Path("data/processed/chunks.json"),
            Path(__file__).resolve().parent.parent.parent / "data" / "processed" / "chunks.json",
        ]
        
        chunks = []
        for p in paths_to_try:
            if p and p.exists():
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        chunks = json.load(f)
                    if chunks:
                        break
                except Exception:
                    pass

        guests = set()
        if isinstance(chunks, list):
            for chunk in chunks:
                g = chunk.get("guest") or chunk.get("metadata", {}).get("guest")
                if g and isinstance(g, str) and len(g.strip()) > 2:
                    clean_g = g.strip()
                    guests.add(clean_g)
                    for word in clean_g.split():
                        if len(word) > 2:
                            self.guest_words.add(word.lower())

        # Fallback default guest list if file not yet loaded
        default_guests = [
            "Ami Vora", "Brian Chesky", "Shreyas Doshi", "Elena Verna", "Casey Winters",
            "Guillermo Rauch", "Boz", "Eric Simons", "Laura Schaffer", "Archie Abrams",
            "Jeff Weinstein", "Paige Costello", "Tamar Yehoshua", "Jules Walter",
            "Anneka Gupta", "Christopher Miller", "Bill Carr", "Howie Liu", "Jag Duggal",
            "Kevin Weil", "Ian McAllister", "Camille Fournier", "NPS", "PLG", "Airbnb", "Faire"
        ]
        for g in default_guests:
            guests.add(g)

        self.known_guests = guests
        self.known_guest_list = list(guests)

    def correct_query(self, query: str) -> Tuple[str, Dict[str, str]]:
        """
        Normalizes misspelled guest names and common typos in user query.
        Returns a tuple of (corrected_query, corrections_dict).
        """
        if not query or not query.strip():
            return query, {}

        corrections: Dict[str, str] = {}
        words = query.strip().split()
        
        # 1. Check 2-word sliding windows against known guest full names
        corrected_words = list(words)
        i = 0
        while i < len(words) - 1:
            pair = f"{words[i]} {words[i+1]}"
            clean_pair = re.sub(r'[^\w\s]', '', pair)
            
            best_match = None
            best_ratio = 0.0

            for guest in self.known_guest_list:
                ratio = SequenceMatcher(None, clean_pair.lower(), guest.lower()).ratio()
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_match = guest

            # High-confidence fuzzy match threshold (>= 0.72) for 2-word names like "Ami Cora" -> "Ami Vora"
            if best_match and best_ratio >= 0.72 and clean_pair.lower() != best_match.lower():
                corrections[clean_pair] = best_match
                # Replace in query preserving trailing punctuation if any
                punct = "".join(c for c in words[i+1] if c in '.,!?:;')
                corrected_words[i] = best_match.split()[0]
                corrected_words[i+1] = best_match.split()[-1] + punct
                i += 2
                continue
            i += 1

        # 2. Check individual single words for guest last names or first names (e.g. "cheskyy" -> "Chesky")
        for idx, word in enumerate(corrected_words):
            clean_w = re.sub(r'[^\w]', '', word)
            if len(clean_w) <= 3 or clean_w.lower() in corrections:
                continue

            best_match = None
            best_ratio = 0.0
            for guest in self.known_guest_list:
                for guest_part in guest.split():
                    if len(guest_part) > 3:
                        ratio = SequenceMatcher(None, clean_w.lower(), guest_part.lower()).ratio()
                        if ratio > best_ratio:
                            best_ratio = ratio
                            best_match = guest_part

            # Single word fuzzy match threshold (>= 0.82)
            if best_match and best_ratio >= 0.82 and clean_w.lower() != best_match.lower():
                punct = "".join(c for c in word if c in '.,!?:;')
                corrections[clean_w] = best_match
                corrected_words[idx] = best_match + punct

        # Reconstruct query
        corrected_query = " ".join(corrected_words)
        
        # 3. Common question typo normalization ("who in" -> "who is", "whos" -> "who is")
        corrected_query = re.sub(r'\bwho\s+in\b', 'who is', corrected_query, flags=re.IGNORECASE)
        corrected_query = re.sub(r'\bwhos\b', 'who is', corrected_query, flags=re.IGNORECASE)
        corrected_query = re.sub(r'\bwhats\b', 'what is', corrected_query, flags=re.IGNORECASE)

        return corrected_query, corrections


# Global singleton instance for fast access
spelling_corrector = SpellingCorrector()
