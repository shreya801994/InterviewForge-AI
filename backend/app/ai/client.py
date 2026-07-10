import logging
from typing import Optional, Type, TypeVar, Any
from google import genai
from google.genai import types
from pydantic import BaseModel

from app.config import settings
from app.ai.models import DEFAULT_MODEL
from app.ai.retry import retry
from app.ai.parser import parse_fallback, AIParsingError

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)

class AIClient:
    _client: Optional[genai.Client] = None

    @classmethod
    def get_client(cls) -> genai.Client:
        if cls._client is None:
            api_key = settings.GEMINI_API_KEY
            if not api_key:
                raise ValueError("GEMINI_API_KEY is not configured in settings")
            cls._client = genai.Client(api_key=api_key)
        return cls._client
        
    @classmethod
    def get_mock_response(cls, prompt: str, schema: Optional[Type[T]] = None) -> Any:
        logger.info("AI_MOCK_MODE enabled. Returning mocked response.")
        if schema and schema.__name__ == "ReportOutput":
            from app.services.evaluation_service import ReportOutput
            return ReportOutput(
                overall_score=8.5,
                strengths=["Great communication", "Strong theoretical foundation"],
                weaknesses=["Needs more practical experience"],
                summary="Solid performance overall.",
                consistency_feedback="Matches resume claims well.",
                roadmap=["Build more projects"]
            )
        elif schema and schema.__name__ == "BaseResumeAnalysisSchema":
            from app.schemas import BaseResumeAnalysisSchema
            return BaseResumeAnalysisSchema(
                skills=["Python", "React"],
                projects=["Mocked Project 1", "Mocked Project 2"],
                strengths=["Quick learner"],
                focus_areas=["System Design"]
            )
        elif schema and schema.__name__ == "ATSSchema":
            from app.schemas import ATSSchema
            return ATSSchema(
                ats_score=85,
                ats_breakdown="Good keywords, clean format.",
                ats_suggestions=["Add more metrics"]
            )
        elif schema and schema.__name__ == "ProjectEvaluationSchema":
            from app.schemas import ProjectEvaluationSchema
            return ProjectEvaluationSchema(
                evaluation="Impressive architecture, well documented."
            )
        elif schema and schema.__name__ == "GenQuestion":
            from app.services.interview_service import GenQuestion
            return GenQuestion(
                question_text="What is a mock object?",
                question_type="conceptual",
                time_limit_seconds=120
            )
        elif schema and schema.__name__ == "GenEvaluation":
            from app.services.interview_service import GenEvaluation
            return GenEvaluation(
                technical_accuracy=9.0,
                communication=8.0,
                depth=7.0,
                feedback="Good answer.",
                next_question="Next mock question?",
                next_question_type="coding",
                next_question_time_limit=300,
                is_completed=False
            )
        return 'Mocked response'

    @classmethod
    @retry(max_retries=3, base_delay=1)
    def generate(cls, prompt: str, schema: Optional[Type[T]] = None, model: str = DEFAULT_MODEL) -> Any:
        if settings.AI_MOCK_MODE:
            import time
            time.sleep(1) # simulate slight delay
            return cls.get_mock_response(prompt, schema)

        client = cls.get_client()
        
        config_kwargs = {
            "temperature": 0.2,
            "max_output_tokens": 4096,
        }
        
        if schema:
            config_kwargs["response_mime_type"] = "application/json"
            config_kwargs["response_schema"] = schema
            
        config = types.GenerateContentConfig(**config_kwargs)
        
        for attempt in range(2):
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=config
            )
            
            if schema:
                if hasattr(response, 'parsed') and response.parsed is not None:
                    return response.parsed
                else:
                    logger.warning("response.parsed was missing, using fallback parser")
                    try:
                        parsed_dict = parse_fallback(response.text)
                        return schema(**parsed_dict)
                    except AIParsingError as e:
                        if attempt == 0:
                            logger.warning(f"JSON Parsing Error detected: {str(e)}. Retrying with formatting prompt.")
                            prompt += "\n\nCRITICAL INSTRUCTION: Your previous response was either truncated because it was too long, or contained invalid JSON. Please provide a significantly more concise response and ensure strictly valid JSON."
                            continue
                        raise
                    
            return response.text
