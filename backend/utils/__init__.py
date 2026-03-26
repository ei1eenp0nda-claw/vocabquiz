# utils/__init__.py
from .prompt_templates import (
    VOCAB_EXTRACTION_PROMPT,
    IMAGE_ANALYSIS_PROMPT,
    get_quiz_generation_prompt
)

__all__ = [
    'VOCAB_EXTRACTION_PROMPT',
    'IMAGE_ANALYSIS_PROMPT',
    'get_quiz_generation_prompt'
]