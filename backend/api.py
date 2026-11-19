from typing import Annotated, Literal

from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend import assistant, knowledge, search
from backend.config import DATA_PATH
from backend.contracts import AnswerResponse, CatalogResponse, QuestionRequest
from backend.errors import ModuleNotReadyError

app = FastAPI(
    title="Citizen Assist AI",
    version="0.1.0",
    description="Coordinator transport scaffold. Core modules are pending. No external AI is used.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.exception_handler(ModuleNotReadyError)
async def handle_pending_module(_request: Request, error: ModuleNotReadyError):
    return JSONResponse(
        status_code=503,
        content={
            "error": "module_pending",
            "module": error.module,
            "detail": str(error),
        },
    )


@app.get("/api/v1/health")
def health():
    return {"status": "ok", "scope": "transport", "externalAi": False}


@app.get("/api/v1/services", response_model=CatalogResponse)
def list_services(
    query: Annotated[str | None, Query(max_length=200)] = None,
    topic: Literal["all", "documents", "work", "social"] = "all",
):
    records = knowledge.load_services(DATA_PATH)
    items = (
        search.search_services(records, query or "", topic)
        if query is not None or topic != "all"
        else records
    )
    return {"items": items, "query": query or ""}


@app.post("/api/v1/assistant/query", response_model=AnswerResponse)
def query_assistant(payload: QuestionRequest):
    records = knowledge.load_services(DATA_PATH)
    return assistant.answer_question(records, payload.question, payload.mode)
