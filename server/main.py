import shutil
import os
import json
from typing import Any, Dict, List, Type, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import the core library
from structure_it.extractors import PolicyRequirementsExtractor, GeminiExtractor
from structure_it.schemas import (
    PolicyRequirements,
    AcademicPaper,
    WebArticle,
    CodeDocumentation,
    MeetingNote,
    MediaTranscript
)
from structure_it.storage.star_schema_storage import StarSchemaStorage
from structure_it.utils.hashing import generate_id

app = FastAPI()

# Initialize Storage
storage = StarSchemaStorage()

# Allow CORS for local UI development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Map generic types to Pydantic Schemas
SCHEMA_MAP: Dict[str, Type[BaseModel]] = {
    "policy": PolicyRequirements,
    "academic": AcademicPaper,
    "article": WebArticle,
    "code": CodeDocumentation,
    "meeting": MeetingNote,
    "media": MediaTranscript
}

# Logic to find start/end indices of a string within the document
def locate_source_indices(full_text: str, snippet: str) -> dict:
    if not snippet or len(snippet) < 10: # Ignore short strings
        return {"start": -1, "end": -1}
        
    # 1. Try exact match
    start = full_text.find(snippet)
    if start != -1:
        return {"start": start, "end": start + len(snippet)}

    # 2. Try matching just the first 50 characters (handling slight LLM hallucinations)
    trunc = snippet[:50]
    start = full_text.find(trunc)
    if start != -1:
        # Estimate end based on statement length
        return {"start": start, "end": start + len(snippet)}

    return {"start": -1, "end": -1}

def recursive_highlight_search(data: Any, full_text: str, path: str = "") -> List[Dict]:
    """Recursively find highlights for all string values in the extraction result."""
    highlights = []
    
    if isinstance(data, dict):
        for key, value in data.items():
            new_path = f"{path}.{key}" if path else key
            highlights.extend(recursive_highlight_search(value, full_text, new_path))
            
    elif isinstance(data, list):
        for i, item in enumerate(data):
            new_path = f"{path}[{i}]"
            highlights.extend(recursive_highlight_search(item, full_text, new_path))
            
    elif isinstance(data, str):
        # Try to find this string in the source text
        loc = locate_source_indices(full_text, data)
        if loc["start"] != -1:
            highlights.append({
                "id": path, # Use the JSON path as the ID
                "start": loc["start"],
                "end": loc["end"],
                "text": data
            })
            
    return highlights

@app.post("/api/extract")
async def extract(
    file: UploadFile = File(...),
    type: str = Form("policy") # Default to policy for backward compatibility
):
    if type not in SCHEMA_MAP:
        raise HTTPException(status_code=400, detail=f"Invalid type. Supported: {list(SCHEMA_MAP.keys())}")

    temp_path = f"temp_{file.filename}"
    try:
        # 1. Save File
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 2. Run structure-it
        meta = {"policy_id": "UPLOAD", "policy_title": file.filename, "policy_type": "General"}
        
        result_model = None
        raw_text = ""

        # Special handling for Policy to keep custom logic
        if type == "policy":
            extractor = PolicyRequirementsExtractor()
            # Use internal method to get text (prototype hack)
            raw_text = extractor._convert_to_markdown(temp_path) 
            result_model = await extractor.extract(temp_path, meta)
        else:
            # Generic handling for other types
            target_schema = SCHEMA_MAP[type]
            # We need a way to get raw text. PolicyRequirementsExtractor has _convert_to_markdown.
            # For now, we instantiate PolicyRequirementsExtractor JUST to get the text converter 
            # because it handles PDFs nicely.
            # In a real app, the text conversion should be a separate utility.
            text_tool = PolicyRequirementsExtractor()
            raw_text = text_tool._convert_to_markdown(temp_path)
            
            # Use Generic Gemini Extractor
            generic_extractor = GeminiExtractor(schema=target_schema)
            result_model = await generic_extractor.extract(content=raw_text)

        # 3. Generate Generic Visual Highlights
        # Convert model to dict
        data_dict = result_model.model_dump()
        highlights = recursive_highlight_search(data_dict, raw_text)

        # 4. Persist to Star Schema Storage
        # Generate a stable ID for the document based on content
        doc_id = generate_id(raw_text)
        await storage.store_entity(
            entity_id=doc_id,
            source_type=type,
            source_url=file.filename,
            raw_content=raw_text,
            structured_data=data_dict,
            metadata=meta
        )

        # 5. Return
        return {
            "raw_text": raw_text,
            "data": data_dict,
            "highlights": highlights,
            "type": type,
            "doc_id": doc_id
        }
        
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.get("/api/search")
async def search(
    q: str = Query(..., description="Search query"),
    filter: Optional[str] = Query(None, description="JSON string of filters")
):
    """Search the Star Schema Knowledge Base."""
    try:
        filters_dict = json.loads(filter) if filter else None
        
        # Placeholder for embedding generation
        # In a real app, we would call an embedding model here
        mock_vector = [0.1] * 768 
        
        results = await storage.retrieve_context(
            query_vector=mock_vector,
            filters=filters_dict,
            limit=20
        )
        
        return {"results": results}
        
    except Exception as e:
        print(f"Search Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
