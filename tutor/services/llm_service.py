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

    AVAILABLE_MODELS = {
        'llama3.2': {
            'name': 'Llama 3.2',
            'provider': 'ollama',
            'model_id': 'llama3.2:latest',
            'description': 'Meta Llama 3.2 - Fast and efficient'
        },
        'gemma3': {
            'name': 'Gemma 3',
            'provider': 'ollama',
            'model_id': 'gemma3:4b',
            'description': 'Google Gemma 3 - Advanced reasoning'
        },
        'gemini': {
            'name': 'Gemini API',
            'provider': 'google',
            'model_id': 'gemini-pro',
            'description': 'Google Gemini - Cloud API (requires key)'
        }
    }

    def __init__(self):
        self.openai_key = getattr(settings, 'OPENAI_API_KEY', '')
        self.anthropic_key = getattr(settings, 'ANTHROPIC_API_KEY', '')
        self.gemini_key = getattr(settings, 'GEMINI_API_KEY', '')
        self.use_cache = True

    def generate_response(
        self,
        messages: List[Dict[str, str]],
        student_grade: int,
        selected_model: str = 'llama3.2',
        use_cache: bool = True
    ) -> Tuple[str, Dict]:
        """
        Generate response using selected LLM

        Args:
            messages: List of message dicts with 'role' and 'content'
            student_grade: Grade level for caching
            selected_model: Model key from AVAILABLE_MODELS
            use_cache: Whether to use cached responses

        Returns:
            Tuple of (response_text, metadata_dict)
        """
        start_time = time.time()

        # Check cache first
        if use_cache and self.use_cache:
            cached_response = self._get_cached_response(messages, student_grade, selected_model)
            if cached_response:
                logger.info("✅ Using cached response")
                return cached_response, {
                    'model': selected_model,
                    'response_time': 0.0,
                    'from_cache': True
                }

        # Get model configuration
        model_config = self.AVAILABLE_MODELS.get(selected_model)
        if not model_config:
            selected_model = 'llama3.2'  # Default fallback
            model_config = self.AVAILABLE_MODELS[selected_model]

        # Try the selected model
        response, metadata = self._try_model(messages, model_config)

        if not response:
            # Try fallback to Llama if primary fails
            if selected_model != 'llama3.2':
                logger.warning(f"{selected_model} failed, trying Llama 3.2 fallback...")
                llama_config = self.AVAILABLE_MODELS['llama3.2']
                response, metadata = self._try_model(messages, llama_config)

        if not response:
            response = "I'm having trouble connecting to my brain right now. Please try again in a moment! 🤖"
            metadata = {'model': 'error', 'response_time': 0.0, 'error': True}

        # Cache the response
        if use_cache and self.use_cache and response and metadata.get('model') != 'error':
            self._cache_response(messages, student_grade, selected_model, response)

        metadata['response_time'] = time.time() - start_time
        return response, metadata

    def _try_model(self, messages: List[Dict[str, str]], model_config: Dict) -> Tuple[Optional[str], Dict]:
        """Try to generate response using specified model"""
        provider = model_config['provider']
        model_id = model_config['model_id']

        try:
            if provider == 'ollama':
                return self._try_ollama_model(messages, model_id)
            elif provider == 'google' and self.gemini_key:
                return self._try_gemini_api(messages, model_id)
            elif provider == 'openai' and self.openai_key:
                return self._try_openai_api(messages)
            elif provider == 'anthropic' and self.anthropic_key:
                return self._try_anthropic_api(messages)
            else:
                logger.warning(f"Provider {provider} not available or missing API key")
                return None, {}

        except Exception as e:
            logger.error(f"Model {model_id} failed: {e}")
            return None, {}

    def _try_ollama_model(self, messages: List[Dict[str, str]], model_id: str) -> Tuple[Optional[str], Dict]:
        """Try to generate response using Ollama model"""
        try:
            logger.info(f"Attempting Ollama with model: {model_id}")

            # Ensure model is available
            try:
                ollama.show(model_id)
            except:
                logger.info(f"Pulling model {model_id}...")
                ollama.pull(model_id)

            response = ollama.chat(
                model=model_id,
                messages=messages,
                options={
                    'temperature': 0.7,
                    'top_p': 0.9,
                    'num_predict': 1024
                }
            )
            answer = response['message']['content']

            return answer, {
                'model': model_id,
                'provider': 'ollama',
                'from_cache': False
            }

        except Exception as e:
            logger.error(f"Ollama model {model_id} failed: {e}")
            return None, {}

    def _try_gemini_api(self, messages: List[Dict[str, str]], model_id: str) -> Tuple[Optional[str], Dict]:
        """Try to generate response using Google Gemini API"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.gemini_key)

            model = genai.GenerativeModel(model_id)

            # Convert messages to Gemini format
            gemini_messages = []
            for msg in messages:
                if msg['role'] == 'system':
                    # Gemini doesn't have system role, add to first user message
                    continue
                elif msg['role'] == 'user':
                    gemini_messages.append({'role': 'user', 'parts': [msg['content']]})
                elif msg['role'] == 'assistant':
                    gemini_messages.append({'role': 'model', 'parts': [msg['content']]})

            # Add system message to first user message if exists
            system_msg = next((m['content'] for m in messages if m['role'] == 'system'), None)
            if system_msg and gemini_messages:
                gemini_messages[0]['parts'][0] = f"{system_msg}\n\n{gemini_messages[0]['parts'][0]}"

            response = model.generate_content(gemini_messages)
            answer = response.text

            return answer, {
                'model': model_id,
                'provider': 'google',
                'from_cache': False
            }

        except Exception as e:
            logger.error(f"Gemini API failed: {e}")
            return None, {}

    def _try_openai_api(self, messages: List[Dict[str, str]]) -> Tuple[Optional[str], Dict]:
        """Try to generate response using OpenAI API"""
        try:
            import openai
            client = openai.OpenAI(api_key=self.openai_key)

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=1024,
                temperature=0.7
            )
            answer = response.choices[0].message.content

            return answer, {
                'model': 'gpt-3.5-turbo',
                'provider': 'openai',
                'from_cache': False
            }
        except Exception as e:
            logger.error(f"OpenAI API failed: {e}")
            return None, {}

    def _try_anthropic_api(self, messages: List[Dict[str, str]]) -> Tuple[Optional[str], Dict]:
        """Try to generate response using Anthropic API"""
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

    def get_available_models(self) -> Dict[str, Dict]:
        """Get list of available models with their status"""
        models_status = {}

        for model_key, model_info in self.AVAILABLE_MODELS.items():
            status = {'available': False, 'reason': ''}

            if model_info['provider'] == 'ollama':
                try:
                    ollama.show(model_info['model_id'])
                    status['available'] = True
                except:
                    status['reason'] = 'Model not downloaded'
            elif model_info['provider'] == 'google':
                status['available'] = bool(self.gemini_key)
                if not status['available']:
                    status['reason'] = 'API key not configured'
            elif model_info['provider'] == 'openai':
                status['available'] = bool(self.openai_key)
                if not status['available']:
                    status['reason'] = 'API key not configured'
            elif model_info['provider'] == 'anthropic':
                status['available'] = bool(self.anthropic_key)
                if not status['available']:
                    status['reason'] = 'API key not configured'

            models_status[model_key] = {
                **model_info,
                **status
            }

        return models_status

    def _generate_cache_key(self, messages: List[Dict], grade: int, model: str) -> str:
        """Generate cache key from messages, grade, and model"""
        # Use last user message for cache key
        user_messages = [m['content'] for m in messages if m['role'] == 'user']
        last_user_msg = user_messages[-1] if user_messages else ""

        # Create hash
        cache_string = f"{last_user_msg}|{grade}|{model}"
        cache_hash = hashlib.md5(cache_string.encode()).hexdigest()
        return f"llm_response_{cache_hash}"

    def _get_cached_response(self, messages: List[Dict], grade: int, model: str) -> Optional[str]:
        """Get cached response if available"""
        cache_key = self._generate_cache_key(messages, grade, model)
        return cache.get(cache_key)

    def _cache_response(self, messages: List[Dict], grade: int, model: str, response: str):
        """Cache the response"""
        cache_key = self._generate_cache_key(messages, grade, model)
        cache.set(cache_key, response, timeout=3600)  # 1 hour


# Singleton instance
_llm_service_instance = None


def get_llm_service() -> LLMService:
    """Get or create LLM service singleton"""
    global _llm_service_instance
    if _llm_service_instance is None:
        _llm_service_instance = LLMService()
    return _llm_service_instance
