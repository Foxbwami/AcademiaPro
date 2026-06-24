"""
Grok AI Service Integration
Handles all interactions with the Grok API for content generation, chat support, and system monitoring
"""

import requests
import json
import os
from typing import Dict, List, Optional
from flask import current_app

class GrokService:
    """Service for interacting with Grok API"""
    
    BASE_URL = "https://api.x.ai/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Grok service with API key"""
        self.api_key = api_key or current_app.config.get('GROK_API_KEY')
        if not self.api_key:
            raise ValueError("GROK_API_KEY not configured")
    
    def _make_request(self, endpoint: str, payload: Dict) -> Dict:
        """Make authenticated request to Grok API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "error": str(e),
                "success": False
            }
    
    def generate_content(self, prompt: str, system_prompt: str, max_tokens: int = 1000) -> Dict:
        """
        Generate content using Grok
        
        Args:
            prompt: User's content request
            system_prompt: System instructions for Grok
            max_tokens: Maximum tokens in response
        
        Returns:
            Dict with generated content or error
        """
        payload = {
            "model": "grok-2",
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
            "temperature": 0.7
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
        Handle multi-turn conversation with Grok
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            system_prompt: System instructions
            max_tokens: Maximum tokens in response
        
        Returns:
            Dict with response or error
        """
        payload = {
            "model": "grok-2",
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                }
            ] + messages,
            "max_tokens": max_tokens,
            "temperature": 0.7
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
        
        return self.generate_content(prompt, system_prompt, max_tokens=2500)


# Singleton instance
_grok_service = None

def get_grok_service() -> GrokService:
    """Get or create Grok service instance"""
    global _grok_service
    if _grok_service is None:
        _grok_service = GrokService()
    return _grok_service
