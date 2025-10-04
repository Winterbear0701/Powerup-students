"""
Tutor Orchestration Service - Main pipeline coordinator
Coordinates RAG, LLM, web scraping, and adaptive learning
"""
import time
import hashlib
from typing import Dict, List, Optional, Tuple
from django.core.cache import cache
import logging

from .rag_service import get_rag_service
from .llm_service import get_llm_service
from .scraping_service import get_scraping_service
from .adaptive_service import get_adaptive_service
from .multimodal_service import get_multimodal_service

logger = logging.getLogger(__name__)


class TutorService:
    """Main orchestration service for the AI Tutor"""
    
    def __init__(self):
        self.rag_service = get_rag_service()
        self.llm_service = get_llm_service()
        self.scraping_service = get_scraping_service()
        self.adaptive_service = get_adaptive_service()
        self.multimodal_service = get_multimodal_service()
    
    def process_query(
        self,
        query: str,
        student_profile: Dict,
        conversation_history: List[Dict] = None,
        include_audio: bool = False,
        include_diagram: bool = True
    ) -> Dict:
        """
        Main query processing pipeline
        
        Args:
            query: User's question
            student_profile: Dict with student info (name, grade, difficulty_level, etc.)
            conversation_history: Previous conversation turns
            include_audio: Whether to generate audio response
            include_diagram: Whether to generate diagrams if applicable
        
        Returns:
            Dict with response, metadata, and multimodal content
        """
        start_time = time.time()
        result = {
            'response': '',
            'sources': [],
            'metadata': {},
            'audio_file': None,
            'diagram_file': None,
            'resource_recommendations': [],
            'processing_time': 0.0
        }
        
        try:
            # Extract student info
            student_name = student_profile.get('name', 'Student')
            grade = student_profile.get('grade', 7)
            difficulty_level = student_profile.get('difficulty_level', 'intermediate')
            struggle_count = student_profile.get('struggle_count', 0)
            
            # Step 1: Detect subject
            subject = self.adaptive_service.detect_subject(query)
            logger.info(f"Detected subject: {subject}")
            
            # Step 2: Retrieve context from RAG
            rag_results = self.rag_service.retrieve_context(
                query=query,
                grade=grade,
                n_results=3,
                subject=subject
            )
            
            context = self.rag_service.format_context_for_prompt(rag_results)
            relevance_score = (
                sum(rag_results.get('relevance_scores', [])) / len(rag_results.get('relevance_scores', [1]))
                if rag_results.get('relevance_scores') else 0.0
            )
            
            logger.info(f"RAG context found: {rag_results['found']}, relevance: {relevance_score:.2f}")
            result['sources'].append('NCERT ChromaDB')
            
            # Step 3: If RAG doesn't find good content, try web scraping
            if not rag_results['found'] or relevance_score < 0.3:
                logger.info("Low RAG relevance, attempting web scraping...")
                
                # Try NCERT website first
                scraped_ncert = self.scraping_service.search_ncert_website(
                    query=query,
                    grade=grade,
                    subject=subject
                )
                
                if scraped_ncert['found']:
                    context += "\n\n--- Web Scraped Content ---\n\n"
                    context += "\n".join(scraped_ncert['content'])
                    result['sources'].extend(scraped_ncert['sources'])
                else:
                    # Try other educational portals
                    scraped_other = self.scraping_service.search_educational_portals(
                        query=query,
                        grade=grade
                    )
                    if scraped_other['found']:
                        context += "\n\n--- Educational Portal Content ---\n\n"
                        context += "\n".join(scraped_other['content'])
                        result['sources'].extend(scraped_other['sources'])
            
            # Step 4: Build adaptive system prompt
            system_prompt = self.adaptive_service.build_system_prompt(
                student_name=student_name,
                grade=grade,
                difficulty_level=difficulty_level,
                subject=subject
            )
            
            # Step 5: Build messages for LLM
            messages = [{'role': 'system', 'content': system_prompt}]
            
            # Add conversation history
            if conversation_history:
                for turn in conversation_history[-3:]:  # Last 3 turns
                    messages.append({'role': 'user', 'content': turn['user']})
                    messages.append({'role': 'assistant', 'content': turn['bot']})
            
            # Add current query with context
            user_prompt = self._build_user_prompt(query, context, grade, subject)
            messages.append({'role': 'user', 'content': user_prompt})
            
            # Step 6: Generate response using LLM
            response, llm_metadata = self.llm_service.generate_response(
                messages=messages,
                student_grade=grade,
                use_cache=True
            )
            
            result['response'] = response
            result['metadata']['llm'] = llm_metadata
            result['metadata']['rag_relevance'] = relevance_score
            result['metadata']['context_found'] = rag_results['found']
            
            # Step 7: Check if resources should be recommended
            if self.adaptive_service.should_recommend_resources(
                query, relevance_score, struggle_count
            ):
                # Get YouTube recommendations
                topic = query[:50]  # Use first part of query as topic
                youtube_recs = self.scraping_service.get_youtube_recommendations(
                    topic=topic,
                    grade=grade
                )
                result['resource_recommendations'] = youtube_recs
            
            # Step 8: Format for exam style if applicable
            if grade >= 9 and subject in ['mathematics', 'science']:
                result['response'] = self.adaptive_service.format_exam_style_answer(
                    content=result['response'],
                    grade=grade,
                    marks=5
                )
            
            # Step 9: Generate audio if requested
            if include_audio:
                audio_path = self.multimodal_service.text_to_speech(
                    text=result['response'][:500]  # Limit audio length
                )
                result['audio_file'] = audio_path
            
            # Step 10: Generate diagram if applicable
            if include_diagram:
                diagram_params = self.multimodal_service.detect_diagram_need(
                    query=query,
                    response=result['response']
                )
                if diagram_params:
                    diagram_path = self.multimodal_service.generate_math_diagram(
                        diagram_type=diagram_params['type'],
                        parameters=diagram_params
                    )
                    result['diagram_file'] = diagram_path
            
            # Step 11: Add suggested next steps
            result['suggestions'] = self.adaptive_service.suggest_next_steps(
                query=query,
                subject=subject,
                grade=grade
            )
            
        except Exception as e:
            logger.error(f"Error processing query: {e}", exc_info=True)
            result['response'] = "I'm sorry, I encountered an error while processing your question. Please try again!"
            result['metadata']['error'] = str(e)
        
        result['processing_time'] = time.time() - start_time
        logger.info(f"Query processed in {result['processing_time']:.2f}s")
        
        return result
    
    def _build_user_prompt(
        self,
        query: str,
        context: str,
        grade: int,
        subject: Optional[str]
    ) -> str:
        """Build the final user prompt with context"""
        
        if not context:
            prompt = f"""I have a question, but I don't have textbook content available right now. 
Please help me understand this using your knowledge:

QUESTION: {query}

Please explain clearly and appropriately for a Class {grade} student."""
        else:
            prompt = f"""Use the following context from NCERT textbooks to answer my question. 
If the context doesn't have the complete answer, you can add from your knowledge, but clearly indicate what's from the textbook vs your explanation.

CONTEXT:
{context}

QUESTION: {query}

Please provide a clear, accurate answer suitable for Class {grade}."""
        
        return prompt
    
    def transcribe_voice_query(self, audio_file_path: str) -> Optional[str]:
        """
        Transcribe voice input to text
        
        Args:
            audio_file_path: Path to audio file
        
        Returns:
            Transcribed text or None
        """
        return self.multimodal_service.transcribe_audio(audio_file_path)


# Singleton instance
_tutor_service_instance = None


def get_tutor_service() -> TutorService:
    """Get or create tutor service singleton"""
    global _tutor_service_instance
    if _tutor_service_instance is None:
        _tutor_service_instance = TutorService()
    return _tutor_service_instance
