from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import os
import hmac
import hashlib
from app.graph_chain import graph_chain

router = APIRouter()

class QueryRequest(BaseModel):
    question: str

@router.post("/webhook", tags=["Webhook"])
async def webhook(request: Request):
    secret = os.getenv("WEBHOOK_SECRET")  

    if not secret:
        raise HTTPException(status_code=401, detail="Unauthorized - Webhook secret not set")

    signature = request.headers.get("X-Hub-Signature-256")

    if not signature:
        raise HTTPException(status_code=401, detail="Signature header missing")

    if signature.startswith("sha256="):
        signature = signature[len("sha256="):]

    body = await request.body()

    expected_signature = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()  

    if not hmac.compare_digest(signature, expected_signature):
        raise HTTPException(status_code=401, detail="Unauthorized for App")

    try:
        data = await request.json()
        question = data.get("question") 

        if not question:
            raise HTTPException(status_code=400, detail="Question is required")

        response = graph_chain.invoke(question)
        return {"response": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))