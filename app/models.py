from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Natural-language hobby question")
    user_id: str = Field(..., min_length=1, description="Caller's user identifier")


class QueryResponse(BaseModel):
    user_id: str
    query: str
    answer: str
