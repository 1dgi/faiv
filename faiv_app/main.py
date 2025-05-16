from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from faiv_app.core import (
    query_faiv, 
    QueryRequest, 
    detect_and_encode_new_insight
)

app = FastAPI()

# CORS handling
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Response schema
class QueryResponse(BaseModel):
    response: str
    new_insight: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "FAIV API is running successfully!"}

@app.post("/query/", response_model=QueryResponse)
async def query(request: QueryRequest):
    try:
        # ✅ Pass the corrected QueryRequest object with session_id
        raw_response = await query_faiv(request)
        new_insight = detect_and_encode_new_insight(raw_response)

        return QueryResponse(
            response=raw_response,
            new_insight=new_insight
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))