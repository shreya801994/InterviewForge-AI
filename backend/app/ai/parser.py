import json
import re
from fastapi import HTTPException, status
from pydantic import BaseModel

class AIParsingError(Exception):
    pass

def strip_markdown(text: str) -> str:
    """Removes markdown code fences from AI response."""
    text = text.strip()
    if "```" in text:
        match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
        if match:
            return match.group(1).strip()
    return text

def parse_json(text: str) -> dict:
    """Validates and parses JSON from AI response."""
    cleaned_text = strip_markdown(text)
    try:
        data = json.loads(cleaned_text)
        if not isinstance(data, dict):
            raise AIParsingError("AI response must be a JSON object")
        return data
    except json.JSONDecodeError as e:
        raise AIParsingError(f"AI returned invalid JSON: {str(e)}")

def parse_fallback(text: str) -> dict:
    """Fallback mechanism to parse JSON if structured output fails."""
    return parse_json(text)

def map_to_schema(data: dict, schema: BaseModel) -> BaseModel:
    """Maps parsed JSON to a Pydantic schema."""
    try:
        return schema(**data)
    except Exception as e:
        raise AIParsingError(f"Schema mapping failed: {str(e)}")
