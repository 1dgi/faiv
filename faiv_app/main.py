from fastapi import FastAPI
from faiv_app.core import query_faiv, QueryRequest  # ✅ Import QueryRequest
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ✅ Add Proper CORS Handling
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Change to frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods: GET, POST, OPTIONS
    allow_headers=["*"],  # Allow all headers
)

@app.get("/")
async def root():
    return {"message": "FAIV API is running successfully!"}

@app.post("/query/")
async def query(request: QueryRequest):
    return await query_faiv(request)
