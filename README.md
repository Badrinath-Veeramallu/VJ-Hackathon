# Sentinel Rx — Prototype

An explainable prescription-safety checker: resolves Indian brand names to
generics, then checks drug-drug, drug-allergy, drug-disease, and
duplicate-therapy risk in one composite, explainable alert — instead of a
flat "interaction detected" label.

This is a **hackathon-ready starting point**, not a finished product. It
runs fully offline (no external API calls) so your demo never depends on
internet access in the room.

## What's actually implemented right now

- ✅ Brand/generic name resolution (exact + fuzzy match)
- ✅ Drug-drug interaction check (graph-based, `networkx`)
- ✅ Drug-allergy check
- ✅ Duplicate-therapy check
- ✅ One drug-disease rule (NSAIDs + renal impairment) as a working example
- ✅ Composite severity scoring across all four risk types
- ✅ Grounded explanation text (facts from the data, not free-form AI)
- ✅ React dashboard that calls the API and renders severity-coded alert cards
- ✅ Unit tests for the core risk engine

## What is NOT yet implemented (be upfront about this with judges)

- ⚠️ **The datasets are small, hand-curated samples**, not the full
  DDInter export or RxNav API integration. `backend/app/data/ddi_sample.json`
  has ~12 well-documented interactions and
  `backend/app/data/brand_generic_map.json` has ~30 common Indian brand
  names. Expand both before relying on this for anything beyond a demo.
- ⚠️ No LLM-polish step is wired up (see `app/explanation.py` —
  `polish_with_llm` is a ready-made hook, not connected to a live model,
  so the demo has zero internet dependency by default).
- ⚠️ No authentication, persistence, or audit log yet — the API is
  stateless per-request.
- ⚠️ Only one drug-disease rule exists as a working example; the real
  system needs a broader rule set.

## Project structure

```
proto/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app + /check-prescription endpoint
│   │   ├── name_resolver.py  # brand/generic fuzzy matching
│   │   ├── graph_engine.py   # multi-factor interaction graph
│   │   ├── explanation.py    # grounded explanation formatting
│   │   ├── models.py         # request/response schemas
│   │   └── data/             # seed datasets (see disclaimer above)
│   ├── tests/
│   │   └── test_graph_engine.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.jsx           # dashboard UI
│   │   ├── index.css
│   │   └── main.jsx
│   ├── package.json
│   └── Dockerfile
└── docker-compose.yml
```

## Quickstart (local, no Docker)

**Backend:**
```bash
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
API docs available at http://localhost:8000/docs (FastAPI auto-generates this).

**Run backend tests:**
```bash
cd backend
python -m unittest tests.test_graph_engine -v
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```
Dashboard available at http://localhost:5173.

## Quickstart (Docker)

```bash
docker compose up --build
```
Backend: http://localhost:8000 · Frontend: http://localhost:5173

## Example API call

```bash
curl -X POST http://localhost:8000/check-prescription \
  -H "Content-Type: application/json" \
  -d '{
    "drugs": ["Ecosprin", "Warf", "Glycomet"],
    "allergies": ["metformin"],
    "diagnoses": ["renal impairment"]
  }'
```

## Where to focus hackathon hours (matches the dev plan in the deck)

1. **Expand `ddi_sample.json`** with more real interactions (source from
   DDInter or RxNav — cite whichever you actually use in your slides).
2. **Expand `brand_generic_map.json`** with the brand names you'll
   actually type live during the demo.
3. **Add the override/audit-log endpoint** (`POST /alerts/{id}/override`)
   — this is one of the differentiators in the pitch, so it should exist
   before judging, even as a simple in-memory list.
4. **Wire `polish_with_llm`** to a real LLM call only if you have time —
   the prototype works, and demos better, without it.
