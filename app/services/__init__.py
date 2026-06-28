"""
Services package for AcademiaPro
Contains business logic for various platform services including AI
"""

from app.services.grok_service import GrokService, get_grok_service
from app.services.ai_prompts import get_system_prompt, get_available_prompts

__all__ = [
    'GrokService',
    'get_grok_service',
    'get_system_prompt',
    'get_available_prompts'
]
