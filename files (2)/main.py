import os
from contextlib import asynccontextmanager
from typing import Any, Optional

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# The port you open in your browser (the OUTSIDE port from `docker run -p`).
# Uvicorn only knows the inside port, so we pass this in ourselves.
PUBLIC_PORT = os.getenv("PUBLIC_PORT", "8000")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs once when the app starts
    print(f"\n>>> Open the app here: http://127.0.0.1:{PUBLIC_PORT}/docs\n", flush=True)
    yield


app = FastAPI(
    title="Request Sender",
    description="Sends HTTP requests and shows the response.",
    lifespan=lifespan,
)


class SendRequest(BaseModel):
    url: str
    method: str = "GET"
    body: Optional[Any] = None  # JSON body, if any


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/send")
async def send(req: SendRequest):
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.request(req.method.upper(), req.url, json=req.body)
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Could not reach {req.url}: {type(e).__name__}")

    try:
        data = r.json()
    except ValueError:
        data = r.text

    return {"status_code": r.status_code, "response": data}