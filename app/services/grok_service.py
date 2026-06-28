"""
Groq AI service integration.
Handles chat completions for content generation, support chat, and system monitoring.
"""

import requests
import json
from typing import Dict, List, Optional
from flask import current_app
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class GrokService:
    """Service for interacting with Groq's OpenAI-compatible API."""
    
    BASE_URL = "https://api.groq.com/openai/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Groq service with API key."""
        self.api_key = api_key or current_app.config.get('GROQ_API_KEY')
        self.model = current_app.config.get('GROQ_MODEL', 'llama-3.3-70b-versatile')
        self.timeout = int(current_app.config.get('GROQ_TIMEOUT', 90))
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not configured")

        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 502, 503, 504],
            allowed_methods=["POST"],
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
    
    def _make_request(self, endpoint: str, payload: Dict) -> Dict:
        """Make authenticated request to Groq API."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            response = self.session.post(url, json=payload, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response is not None else "unknown"
            body = e.response.text if e.response is not None else str(e)
            return {
                "error": f"Groq API HTTP {status_code}: {body}",
                "success": False
            }
        except requests.exceptions.ConnectionError as e:
            return {
                "error": f"Groq API connection failed: {str(e)}",
                "success": False
            }
        except requests.exceptions.Timeout as e:
            return {
                "error": f"Groq API timeout: {str(e)}",
                "success": False
            }
        except requests.exceptions.RequestException as e:
            return {
                "error": f"Groq API request failed: {str(e)}",
                "success": False
            }
    
    def generate_content(self, prompt: str, system_prompt: str, max_tokens: int = 1000) -> Dict:
        """
        Generate content using Groq
        
        Args:
            prompt: User's content request
            system_prompt: System instructions for Groq
            max_tokens: Maximum tokens in response
        
        Returns:
            Dict with generated content or error
        """
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": max_tokens,
            "temperature": 0.2,
            "top_p": 0.9,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0
        }
        
        response = self._make_request("/chat/completions", payload)
        
        if response.get("error"):
            return {
                "success": False,
                "error": response.get("error"),
                "content": None
            }
        
        try:
            content = response['choices'][0]['message']['content']
            return {
                "success": True,
                "content": content,
                "error": None
            }
        except (KeyError, IndexError):
            return {
                "success": False,
                "error": "Unexpected API response format",
                "content": None
            }
    
    def chat_message(self, messages: List[Dict], system_prompt: str, max_tokens: int = 1000) -> Dict:
        """
        Handle multi-turn conversation with Groq
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            system_prompt: System instructions
            max_tokens: Maximum tokens in response
        
        Returns:
            Dict with response or error
        """
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                }
            ] + messages,
            "max_tokens": max_tokens,
            "temperature": 0.2,
            "top_p": 0.9,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0
        }
        
        response = self._make_request("/chat/completions", payload)
        
        if response.get("error"):
            return {
                "success": False,
                "error": response.get("error"),
                "content": None
            }
        
        try:
            content = response['choices'][0]['message']['content']
            return {
                "success": True,
                "content": content,
                "error": None
            }
        except (KeyError, IndexError):
            return {
                "success": False,
                "error": "Unexpected API response format",
                "content": None
            }
    
    def analyze_system_performance(self, metrics: Dict) -> Dict:
        """
        Analyze system performance metrics and provide recommendations
        
        Args:
            metrics: Dict with system performance data
        
        Returns:
            Dict with analysis and recommendations
        """
        system_prompt = """You are an expert system administrator analyzing AcademiaPro platform performance.

CRITICAL INSTRUCTIONS:
1. Provide COMPLETE analysis of ALL metrics provided - analyze each one
2. Do not abbreviate or skip any metrics
3. Provide thorough assessment, not brief snippets
4. Include detailed recommendations with full explanations
5. Address each concern completely

Provide actionable insights and recommendations based on ALL metrics provided.
Be thorough and detailed in your analysis."""
        
        prompt = f"""Analyze EVERY system metric provided below and provide comprehensive insights:
        
{json.dumps(metrics, indent=2)}

Please provide:
1. Performance assessment (Good/Fair/Poor) with full explanation
2. All key concerns identified (not just main ones)
3. Detailed recommendations for improvement with explanations
4. Priority actions with complete details"""
        
        max_tokens = int(current_app.config.get('GROQ_MAX_TOKENS', 6000))
        return self.generate_content(prompt, system_prompt, max_tokens=max_tokens)


# Singleton instance
_grok_service = None

def get_grok_service() -> GrokService:
    """Get or create Groq service instance."""
    global _grok_service
    api_key = current_app.config.get('GROQ_API_KEY')
    model = current_app.config.get('GROQ_MODEL', 'llama-3.3-70b-versatile')
    if (
        _grok_service is None
        or _grok_service.api_key != api_key
        or _grok_service.model != model
    ):
        _grok_service = GrokService()
    return _grok_service
