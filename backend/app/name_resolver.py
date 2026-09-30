"""
Drug-name resolution layer.

Real Indian prescriptions mix brand names, generic names, and misspellings.
This module normalizes whatever a clinician typed into a single generic
drug identifier so the interaction graph never has to deal with raw text.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Optional

from rapidfuzz import process, fuzz

DATA_DIR = Path(__file__).parent / "data"


class NameResolver:
    def __init__(self, brand_map_path: Path = DATA_DIR / "brand_generic_map.json"):
        with open(brand_map_path, encoding="utf-8") as f:
            self.brand_to_generic: dict[str, str] = json.load(f)

        # Build the universe of known names (brands + generics) for fuzzy matching
        self.known_generics = set(self.brand_to_generic.values())
        self.all_known_names = list(self.brand_to_generic.keys()) + list(self.known_generics)

    def resolve(self, raw_name: str, fuzzy_threshold: int = 82) -> dict:
        """
        Resolve a free-text drug name to a standardized generic id.

        Returns a dict describing how confident the match was, so the
        frontend can show "resolved via exact match" vs "resolved via
        fuzzy match — please confirm" rather than silently guessing.
        """
        cleaned = raw_name.strip().lower()

        # 1. Exact generic match
        if cleaned in self.known_generics:
            return {
                "input": raw_name,
                "generic": cleaned,
                "match_type": "exact_generic",
                "confidence": 100,
            }

        # 2. Exact brand match
        if cleaned in self.brand_to_generic:
            return {
                "input": raw_name,
                "generic": self.brand_to_generic[cleaned],
                "match_type": "exact_brand",
                "confidence": 100,
            }

        # 3. Fuzzy match against the full known-name universe
        match = process.extractOne(
            cleaned, self.all_known_names, scorer=fuzz.WRatio
        )
        if match and match[1] >= fuzzy_threshold:
            matched_name, score, _ = match
            generic = self.brand_to_generic.get(matched_name, matched_name)
            return {
                "input": raw_name,
                "generic": generic,
                "match_type": "fuzzy",
                "matched_against": matched_name,
                "confidence": round(score, 1),
            }

        # 4. Unknown — never silently drop a drug, flag it instead
        return {
            "input": raw_name,
            "generic": None,
            "match_type": "unknown",
            "confidence": 0,
        }
