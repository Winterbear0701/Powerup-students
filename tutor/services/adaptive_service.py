"""
Adaptive Learning Service - Personalized teaching strategies
Handles grade-specific prompt engineering and difficulty adjustment
"""
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class AdaptiveLearningService:
    """Service for adaptive learning and personalized responses"""
    
    def __init__(self):
        # Grade-specific teaching strategies
        self.grade_strategies = {
            5: {
                'level': 'beginner',
                'style': 'fun_and_games',
                'complexity': 'very_simple',
                'examples': 'everyday_life'
            },
            6: {
                'level': 'beginner',
                'style': 'fun_and_games',
                'complexity': 'simple',
                'examples': 'everyday_life'
            },
            7: {
                'level': 'intermediate',
                'style': 'guided_learning',
                'complexity': 'moderate',
                'examples': 'practical_scenarios'
            },
            8: {
                'level': 'intermediate',
                'style': 'guided_learning',
                'complexity': 'moderate',
                'examples': 'practical_scenarios'
            },
            9: {
                'level': 'advanced',
                'style': 'exam_focused',
                'complexity': 'detailed',
                'examples': 'exam_questions'
            },
            10: {
                'level': 'advanced',
                'style': 'exam_focused',
                'complexity': 'detailed',
                'examples': 'exam_questions'
            }
        }
    
    def build_system_prompt(
        self,
        student_name: str,
        grade: int,
        difficulty_level: str = 'intermediate',
        subject: Optional[str] = None
    ) -> str:
        """
        Build grade-appropriate system prompt
        
        Args:
            student_name: Student's name
            grade: Grade level (5-10)
            difficulty_level: Current difficulty level
            subject: Optional subject context
        
        Returns:
            Personalized system prompt
        """
        strategy = self.grade_strategies.get(grade, self.grade_strategies[7])
        
        # Base prompt
        base_prompt = f"You are a friendly and expert NCERT AI Tutor helping {student_name}, a Class {grade} student."
        
        # Grade-specific instructions
        if grade in [5, 6]:
            teaching_style = f"""
Your teaching style for Class {grade}:
- Use FUN stories, games, and simple analogies to explain concepts
- Make learning feel like an adventure or puzzle
- Use emojis and friendly language
- Break down concepts into tiny, digestible pieces
- Relate everything to things {student_name} sees in daily life
- Always encourage and celebrate their curiosity
- If explaining math, use real objects (toys, fruits, etc.)
- Avoid technical jargon completely
"""
        
        elif grade in [7, 8]:
            teaching_style = f"""
Your teaching style for Class {grade}:
- Provide STEP-BY-STEP guided solutions with clear examples
- Use practical real-world scenarios to explain concepts
- Show the "why" behind each step
- Use simple diagrams or visual descriptions when helpful
- For math problems, show each calculation clearly
- For science, explain cause-and-effect relationships
- Build on their existing knowledge gradually
- Encourage them to think critically
"""
        
        else:  # Grade 9-10
            teaching_style = f"""
Your teaching style for Class {grade}:
- Provide EXAM-ORIENTED, detailed explanations
- Break solutions into clear steps as if writing an answer key
- Show proper formula usage and derivations
- Explain marking scheme logic (which steps get marks)
- Use standard NCERT terminology and notation
- For math: Show all working, formulas, and final answers clearly
- For science: Include definitions, diagrams, and scientific reasoning
- Highlight important concepts that frequently appear in exams
"""
        
        # Difficulty adjustment
        difficulty_instruction = ""
        if difficulty_level == 'beginner':
            difficulty_instruction = "\n⚠️ IMPORTANT: This student is struggling. Use the SIMPLEST possible explanation. Break it down into even smaller steps."
        elif difficulty_level == 'advanced':
            difficulty_instruction = "\n✨ This student is doing well! You can include additional insights and advanced concepts."
        
        # Subject-specific additions
        subject_instruction = ""
        if subject:
            if subject.lower() in ['math', 'mathematics']:
                subject_instruction = "\n📐 For math problems: Show ALL steps, formulas, and calculations clearly."
            elif subject.lower() in ['science', 'physics', 'chemistry', 'biology']:
                subject_instruction = "\n🔬 For science: Include definitions, examples, and real-world applications."
        
        # Resource recommendation instruction
        resource_instruction = """
If the concept is too complex or {student_name} might need more help:
- Recommend helpful YouTube videos (Khan Academy, NCERT official, etc.)
- Suggest NCERT website links for additional reading
- Provide practice problem suggestions
"""
        
        # Combine all parts
        full_prompt = f"""{base_prompt}

{teaching_style}

{difficulty_instruction}

{subject_instruction}

{resource_instruction}

Remember to:
1. Always address {student_name} by name
2. Be encouraging and positive
3. Ask if they understood at the end
4. Offer to explain differently if needed
"""
        
        return full_prompt.strip()
    
    def detect_subject(self, query: str) -> Optional[str]:
        """
        Detect subject from query
        
        Args:
            query: User's question
        
        Returns:
            Detected subject or None
        """
        query_lower = query.lower()
        
        # Math keywords
        math_keywords = ['add', 'subtract', 'multiply', 'divide', 'equation', 'solve', 'calculate',
                        'fraction', 'percentage', 'geometry', 'algebra', 'triangle', 'area', 'volume']
        if any(keyword in query_lower for keyword in math_keywords):
            return 'mathematics'
        
        # Science keywords
        science_keywords = ['experiment', 'reaction', 'chemical', 'physics', 'force', 'energy',
                           'cell', 'biology', 'organism', 'atom', 'molecule', 'photosynthesis']
        if any(keyword in query_lower for keyword in science_keywords):
            return 'science'
        
        # Social studies keywords
        social_keywords = ['history', 'geography', 'government', 'democracy', 'map', 'river',
                          'mountain', 'civilization', 'independence', 'constitution']
        if any(keyword in query_lower for keyword in social_keywords):
            return 'social_studies'
        
        return None
    
    def should_recommend_resources(
        self,
        query: str,
        context_relevance: float,
        student_struggle_count: int
    ) -> bool:
        """
        Determine if we should recommend external resources
        
        Args:
            query: User's question
            context_relevance: RAG context relevance score
            student_struggle_count: Number of times student struggled
        
        Returns:
            True if resources should be recommended
        """
        # Low relevance from RAG
        if context_relevance < 0.3:
            return True
        
        # Student is struggling
        if student_struggle_count >= 2:
            return True
        
        # Complex query indicators
        complex_keywords = ['prove', 'derive', 'explain in detail', 'why', 'how does']
        if any(keyword in query.lower() for keyword in complex_keywords):
            return True
        
        return False
    
    def format_exam_style_answer(
        self,
        content: str,
        grade: int,
        marks: int = 5
    ) -> str:
        """
        Format answer in exam style with proper structure
        
        Args:
            content: Raw answer content
            grade: Student's grade
            marks: Marks for the question
        
        Returns:
            Formatted exam-style answer
        """
        if grade < 9:
            return content  # No special formatting for lower grades
        
        # Add exam-style structure
        formatted = f"""
📝 **Answer:** (Suggested marks: {marks})

{content}

---
💡 **Note:** In your exam, remember to:
- Write clear headings/subheadings
- Show all steps and formulas
- Draw diagrams if asked
- Write definitions exactly as in NCERT
- Check your answer once completed
"""
        return formatted.strip()
    
    def suggest_next_steps(
        self,
        query: str,
        subject: Optional[str],
        grade: int
    ) -> List[str]:
        """
        Suggest follow-up questions or practice items
        
        Args:
            query: Current query
            subject: Detected subject
            grade: Student's grade
        
        Returns:
            List of suggested next steps
        """
        suggestions = []
        
        if subject == 'mathematics':
            suggestions = [
                "Would you like to see a similar problem to practice?",
                "Shall I explain any specific step in more detail?",
                "Want to try solving a practice question on this topic?"
            ]
        elif subject == 'science':
            suggestions = [
                "Would you like to see a diagram for this concept?",
                "Shall I explain the real-world applications?",
                "Want to know common exam questions on this topic?"
            ]
        else:
            suggestions = [
                "Do you have any follow-up questions?",
                "Would you like more examples?",
                "Shall I recommend some videos to watch?"
            ]
        
        return suggestions


# Singleton instance
_adaptive_service_instance = None


def get_adaptive_service() -> AdaptiveLearningService:
    """Get or create adaptive learning service singleton"""
    global _adaptive_service_instance
    if _adaptive_service_instance is None:
        _adaptive_service_instance = AdaptiveLearningService()
    return _adaptive_service_instance
