"""
Multi-factor interaction graph.

This is the core differentiator: instead of a single drug-drug lookup,
every prescription is checked against several risk types in one pass,
and every alert is traceable back to a specific graph fact — nothing
here is generated freely by a language model.
"""
from __future__ import annotations
import json
from pathlib import Path
from itertools import combinations

import networkx as nx

DATA_DIR = Path(__file__).parent / "data"

SEVERITY_RANK = {"critical": 3, "high": 2, "moderate": 1, "low": 0}


class InteractionGraph:
    def __init__(self, ddi_path: Path = DATA_DIR / "ddi_sample.json"):
        with open(ddi_path, encoding="utf-8") as f:
            self.ddi_records: list[dict] = json.load(f)

        self.graph = nx.Graph()
        for rec in self.ddi_records:
            self.graph.add_edge(
                rec["drug_a"],
                rec["drug_b"],
                severity=rec["severity"],
                mechanism=rec["mechanism"],
                recommendation=rec["recommendation"],
            )

    # ---- Drug-drug interaction check -------------------------------------
    def check_drug_pairs(self, generics: list[str]) -> list[dict]:
        alerts = []
        for a, b in combinations(sorted(set(generics)), 2):
            if self.graph.has_edge(a, b):
                data = self.graph.get_edge_data(a, b)
                alerts.append({
                    "type": "drug_drug",
                    "drugs": [a, b],
                    "severity": data["severity"],
                    "explanation": (
                        f"{a.title()} + {b.title()}: {data['mechanism']}"
                    ),
                    "recommendation": data["recommendation"],
                })
        return alerts

    # ---- Duplicate therapy check ------------------------------------------
    @staticmethod
    def check_duplicate_therapy(generics: list[str]) -> list[dict]:
        alerts = []
        seen = {}
        for g in generics:
            seen[g] = seen.get(g, 0) + 1
        for drug, count in seen.items():
            if count > 1:
                alerts.append({
                    "type": "duplicate_therapy",
                    "drugs": [drug],
                    "severity": "moderate",
                    "explanation": f"{drug.title()} appears {count} times in this prescription.",
                    "recommendation": "Confirm this is not an unintentional duplicate order.",
                })
        return alerts

    # ---- Drug-allergy check ------------------------------------------------
    @staticmethod
    def check_allergies(generics: list[str], allergies: list[str]) -> list[dict]:
        alerts = []
        allergy_set = {a.strip().lower() for a in allergies if a.strip()}
        for g in generics:
            if g in allergy_set:
                alerts.append({
                    "type": "drug_allergy",
                    "drugs": [g],
                    "severity": "critical",
                    "explanation": f"Patient has a documented allergy to {g.title()}.",
                    "recommendation": "Do not dispense. Select an alternative agent.",
                })
        return alerts

    # ---- Drug-disease contraindication check (simple keyword rules) -------
    DISEASE_CONTRAINDICATIONS = {
        ("nsaid_class", "renal_impairment"): {
            "severity": "high",
            "explanation": "NSAIDs can worsen renal function in patients with existing renal impairment.",
            "recommendation": "Avoid NSAIDs; consider paracetamol or a renally-safer alternative.",
        },
    }
    NSAID_DRUGS = {"ibuprofen", "diclofenac", "naproxen"}

    def check_drug_disease(self, generics: list[str], diagnoses: list[str]) -> list[dict]:
        alerts = []
        diag_set = {d.strip().lower().replace(" ", "_") for d in diagnoses if d.strip()}
        if diag_set & {"renal_impairment", "ckd", "chronic_kidney_disease"}:
            for g in generics:
                if g in self.NSAID_DRUGS:
                    rule = self.DISEASE_CONTRAINDICATIONS[("nsaid_class", "renal_impairment")]
                    alerts.append({
                        "type": "drug_disease",
                        "drugs": [g],
                        "severity": rule["severity"],
                        "explanation": rule["explanation"],
                        "recommendation": rule["recommendation"],
                    })
        return alerts

    # ---- Composite check ----------------------------------------------------
    def check_all(self, generics: list[str], allergies: list[str], diagnoses: list[str]) -> dict:
        known = [g for g in generics if g]
        alerts = (
            self.check_drug_pairs(known)
            + self.check_duplicate_therapy(known)
            + self.check_allergies(known, allergies)
            + self.check_drug_disease(known, diagnoses)
        )
        alerts.sort(key=lambda a: SEVERITY_RANK.get(a["severity"], 0), reverse=True)
        overall = alerts[0]["severity"] if alerts else "none"
        return {
            "overall_severity": overall,
            "alert_count": len(alerts),
            "alerts": alerts,
        }
