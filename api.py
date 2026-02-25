"""Optional FastAPI web server for Suno Prompt Architect.

Run with:
    uvicorn api:app --reload

Swagger UI: http://localhost:8000/docs
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ValidationError as PydanticValidationError

from core.models import PromptInput, ValidationError
from core.engine import generate_prompt

app = FastAPI(
    title="Suno Prompt Architect API",
    description="Generate deterministic Suno AI v5 prompts via REST.",
    version="1.0.0",
)


class GenerateRequest(BaseModel):
    genre: str
    mood: str
    tempo: str
    vocal_type: str
    energy: Optional[str] = None
    instruments: list[str] = []
    production: Optional[str] = None
    structure_hints: Optional[str] = None


class GenerateResponse(BaseModel):
    prompt: str
    char_count: int
    truncated_items: list[str]
    warnings: list[str]


@app.post("/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest):
    """Generate a Suno prompt from musical parameters."""
    try:
        inp = PromptInput(**req.model_dump())
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    result = generate_prompt(inp)
    return GenerateResponse(
        prompt=result.prompt,
        char_count=result.char_count,
        truncated_items=result.truncated_items,
        warnings=result.warnings,
    )


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok"}
