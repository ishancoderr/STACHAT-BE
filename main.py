from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.webhook import router as webhook_router

app = FastAPI(
    title="STACHAT",
    version="1.0.0.v",
    description="API for querying datasets using LangChain and Neo4j."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhook_router)

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to STACHAT!"}
