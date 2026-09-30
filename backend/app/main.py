from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .models import PrescriptionCheckRequest, PrescriptionCheckResponse, ResolvedDrug
from .name_resolver import NameResolver
from .graph_engine import InteractionGraph
from .explanation import format_all

app = FastAPI(
    title="Sentinel Rx API",
    description="Explainable prescription-safety checking — drug-drug, drug-allergy, "
                 "drug-disease, and duplicate-therapy risk in one composite check.",
    version="0.1.0",
)

# Allow the local dashboard (Vite dev server) to call this API during the hackathon
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

resolver = NameResolver()
graph = InteractionGraph()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/check-prescription", response_model=PrescriptionCheckResponse)
def check_prescription(req: PrescriptionCheckRequest):
    resolved = [resolver.resolve(d) for d in req.drugs]
    generics = [r["generic"] for r in resolved if r["generic"]]

    result = graph.check_all(
        generics=generics,
        allergies=req.allergies,
        diagnoses=req.diagnoses,
    )
    result["alerts"] = format_all(result["alerts"])

    return PrescriptionCheckResponse(
        resolved_drugs=[ResolvedDrug(**r) for r in resolved],
        overall_severity=result["overall_severity"],
        alert_count=result["alert_count"],
        alerts=result["alerts"],
    )
