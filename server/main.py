import shutil
import os
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
# Import the core library
from structure_it.extractors import PolicyRequirementsExtractor

app = FastAPI()

# Allow CORS for local UI development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logic to find start/end indices of a string within the document
# This enables the "X-Ray" highlighting feature
def locate_source_indices(full_text: str, statement: str) -> dict:
    # 1. Try exact match
    start = full_text.find(statement)
    if start != -1:
        return {"start": start, "end": start + len(statement)}

    # 2. Try matching just the first 50 characters (handling slight LLM hallucinations)
    snippet = statement[:50]
    start = full_text.find(snippet)
    if start != -1:
        # Estimate end based on statement length
        return {"start": start, "end": start + len(statement)}

    return {"start": -1, "end": -1}

@app.post("/api/extract")
async def extract(file: UploadFile = File(...)):
    temp_path = f"temp_{file.filename}"
    try:
        # 1. Save File
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 2. Run structure-it
        # Mock metadata typically required by the library
        meta = {"policy_id": "UPLOAD", "policy_title": file.filename, "policy_type": "General"}
        extractor = PolicyRequirementsExtractor()

        # Get raw text AND structured data
        raw_text = extractor._convert_to_markdown(temp_path)
        result = await extractor.extract(temp_path, meta)

        # 3. Generate Visual Highlights
        highlights = []
        for req in result.requirements:
            loc = locate_source_indices(raw_text, req.statement)
            if loc["start"] != -1:
                highlights.append({
                    "id": req.requirement_id,
                    "start": loc["start"],
                    "end": loc["end"]
                })

        return {
            "raw_text": raw_text,
            "data": result.model_dump(),
            "highlights": highlights
        }
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
