import logging
import os

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader

load_dotenv()  # no-op when env vars are already set (e.g. in production)

from app.models import QueryRequest, QueryResponse
from app.services.llm_service import answer_hobby_query

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="HobbyIQ Conductor",
    description="AI-powered conductor for sports-card and collectibles hobby queries.",
    version="1.0.0",
)

_raw_origins = os.environ.get("ALLOWED_ORIGINS", "*")
_origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization", "Ocp-Apim-Subscription-Key"],
)

_apim_header = APIKeyHeader(name="Ocp-Apim-Subscription-Key", auto_error=False)


def verify_subscription_key(key: str = Security(_apim_header)) -> None:
    """Validate the incoming Ocp-Apim-Subscription-Key when CONDUCTOR_SUBSCRIPTION_KEY is set."""
    expected = os.environ.get("CONDUCTOR_SUBSCRIPTION_KEY")
    if expected and key != expected:
        raise HTTPException(status_code=401, detail="Invalid or missing subscription key")


@app.get("/health")
def health_check():
    """Liveness / readiness probe used by Azure Container Apps."""
    return {"status": "ok"}


@app.post("/api/v1/query", response_model=QueryResponse, dependencies=[Depends(verify_subscription_key)])
def query(request: QueryRequest):
    """Accept a natural-language hobby question and return an AI-generated answer."""
    logger.info("query user_id=%s query=%r", request.user_id, request.query)
    try:
        answer = answer_hobby_query(request.query)
    except Exception as exc:
        logger.exception("LLM call failed: %s", exc)
        raise HTTPException(status_code=502, detail="Upstream AI service error") from exc

    return QueryResponse(user_id=request.user_id, query=request.query, answer=answer)


@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
