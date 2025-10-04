"""
LLM Service - Language Model Integration
Supports Ollama (local) with API fallback (OpenAI/Anthropic)
"""
import ollama
import time
import hashlib
from django.conf import settings
from django.core.cache import cache
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class LLMService:
    """Service for generating responses using LLMs"""
    
    def __init__(self):
        self.ollama_model = settings.OLLAMA_MODEL
        self.ollama_fallback = settings.OLLAMA_FALLBACK_MODEL
        self.openai_key = settings.OPENAI_API_KEY
        self.anthropic_key = settings.ANTHROPIC_API_KEY
        self.use_cache = True
    
    def generate_response(
        self,
        messages: List[Dict[str, str]],
        student_grade: int,
        use_cache: bool = True
    ) -> Tuple[str, Dict]:
        """
        Generate response using available LLM
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            student_grade: Grade level for caching
            use_cache: Whether to use cached responses
        
        Returns:
            Tuple of (response_text, metadata_dict)
        """
        start_time = time.time()
        
        # Check cache first
        if use_cache and self.use_cache:
            cached_response = self._get_cached_response(messages, student_grade)
            if cached_response:
                logger.info("✅ Using cached response")
                return cached_response, {
                    'model': 'cached',
                    'response_time': 0.0,
                    'from_cache': True
                }
        
        # Try Ollama first
        response, metadata = self._try_ollama(messages)
        
        # Fallback to API if Ollama fails
        if not response and (self.openai_key or self.anthropic_key):
            logger.warning("Ollama failed, trying API fallback...")
            response, metadata = self._try_api_fallback(messages)
        
        if not response:
            response = "I'm having trouble connecting to my brain right now. Please try again in a moment! 🤖"
            metadata = {'model': 'error', 'response_time': 0.0, 'error': True}
        
        # Cache the response
        if use_cache and self.use_cache and response:
            self._cache_response(messages, student_grade, response)
        
        metadata['response_time'] = time.time() - start_time
        return response, metadata
    
    def _try_ollama(self, messages: List[Dict[str, str]]) -> Tuple[Optional[str], Dict]:
        """Try to generate response using Ollama"""
        try:
            logger.info(f"Attempting Ollama with model: {self.ollama_model}")
            response = ollama.chat(
                model=self.ollama_model,
                messages=messages
            )
            answer = response['message']['content']
            
            return answer, {
                'model': self.ollama_model,
                'provider': 'ollama',
                'from_cache': False
            }
            
        except Exception as e:
            logger.error(f"Ollama primary model failed: {e}")
            
            # Try fallback model
            if self.ollama_fallback and self.ollama_fallback != self.ollama_model:
                try:
                    logger.info(f"Trying Ollama fallback: {self.ollama_fallback}")
                    response = ollama.chat(
                        model=self.ollama_fallback,
                        messages=messages
                    )
                    answer = response['message']['content']
                    
                    return answer, {
                        'model': self.ollama_fallback,
                        'provider': 'ollama',
                        'from_cache': False
                    }
                except Exception as e2:
                    logger.error(f"Ollama fallback model failed: {e2}")
            
            return None, {}
    
    def _try_api_fallback(self, messages: List[Dict[str, str]]) -> Tuple[Optional[str], Dict]:
        """Try to generate response using API services"""
        # Try OpenAI
        if self.openai_key:
            try:
                import openai
                openai.api_key = self.openai_key
                
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=messages
                )
                answer = response.choices[0].message.content
                
                return answer, {
                    'model': 'gpt-3.5-turbo',
                    'provider': 'openai',
                    'from_cache': False
                }
            except Exception as e:
                logger.error(f"OpenAI API failed: {e}")
        
        # Try Anthropic
        if self.anthropic_key:
            try:
                import anthropic
                client = anthropic.Anthropic(api_key=self.anthropic_key)
                
                # Convert messages format
                system_msg = next((m['content'] for m in messages if m['role'] == 'system'), None)
                other_messages = [m for m in messages if m['role'] != 'system']
                
                response = client.messages.create(
                    model="claude-3-haiku-20240307",
                    system=system_msg,
                    messages=other_messages,
                    max_tokens=1024
                )
                answer = response.content[0].text
                
                return answer, {
                    'model': 'claude-3-haiku',
                    'provider': 'anthropic',
                    'from_cache': False
                }
            except Exception as e:
                logger.error(f"Anthropic API failed: {e}")
        
        return None, {}
    
    def _generate_cache_key(self, messages: List[Dict], grade: int) -> str:
        """Generate cache key from messages and grade"""
        # Use last user message for cache key
        user_messages = [m['content'] for m in messages if m['role'] == 'user']
        last_user_msg = user_messages[-1] if user_messages else ""
        
        # Create hash
        cache_string = f"{last_user_msg}|{grade}"
        cache_hash = hashlib.md5(cache_string.encode()).hexdigest()
        return f"llm_response_{cache_hash}"
    
    def _get_cached_response(self, messages: List[Dict], grade: int) -> Optional[str]:
        """Get cached response if available"""
        cache_key = self._generate_cache_key(messages, grade)
        return cache.get(cache_key)
    
    def _cache_response(self, messages: List[Dict], grade: int, response: str):
        """Cache the response"""
        cache_key = self._generate_cache_key(messages, grade)
        cache.set(cache_key, response, timeout=3600)  # 1 hour


# Singleton instance
_llm_service_instance = None


def get_llm_service() -> LLMService:
    """Get or create LLM service singleton"""
    global _llm_service_instance
    if _llm_service_instance is None:
        _llm_service_instance = LLMService()
    return _llm_service_instance
