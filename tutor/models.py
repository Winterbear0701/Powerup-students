from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json


class StudentProfile(models.Model):
    """Extended user profile for students"""
    GRADE_CHOICES = [(i, f'Class {i}') for i in range(5, 11)]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    name = models.CharField(max_length=100)
    age = models.IntegerField(null=True, blank=True)
    grade = models.IntegerField(choices=GRADE_CHOICES, default=5)
    
    # Adaptive Learning Metrics
    total_queries = models.IntegerField(default=0)
    successful_interactions = models.IntegerField(default=0)
    struggle_count = models.IntegerField(default=0)  # Times needed simpler explanations
    current_difficulty_level = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced')
        ],
        default='intermediate'
    )
    
    # Preferences
    preferred_learning_style = models.CharField(
        max_length=20,
        choices=[
            ('visual', 'Visual'),
            ('auditory', 'Auditory'),
            ('text', 'Text-based'),
            ('mixed', 'Mixed')
        ],
        default='mixed'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} (Class {self.grade})"
    
    def adjust_difficulty(self, success: bool):
        """Adjust difficulty level based on user performance"""
        if not success:
            self.struggle_count += 1
            if self.struggle_count >= 3 and self.current_difficulty_level != 'beginner':
                levels = ['advanced', 'intermediate', 'beginner']
                current_index = levels.index(self.current_difficulty_level)
                self.current_difficulty_level = levels[min(current_index + 1, 2)]
                self.struggle_count = 0
        else:
            self.successful_interactions += 1
            if self.successful_interactions >= 5 and self.current_difficulty_level != 'advanced':
                levels = ['beginner', 'intermediate', 'advanced']
                current_index = levels.index(self.current_difficulty_level)
                self.current_difficulty_level = levels[min(current_index + 1, 2)]
                self.successful_interactions = 0
        self.save()


class Conversation(models.Model):
    """Stores conversation sessions"""
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='conversations')
    session_id = models.CharField(max_length=100, unique=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Conversation {self.session_id} - {self.student.name}"


class Message(models.Model):
    """Individual messages in a conversation"""
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System')
    ]
    
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    
    # Metadata
    retrieval_context = models.TextField(blank=True, null=True)  # RAG context used
    scraped_sources = models.TextField(blank=True, null=True)  # Web scraped sources
    llm_model_used = models.CharField(max_length=50, blank=True, null=True)
    response_time = models.FloatField(null=True, blank=True)  # seconds
    
    # Multimodal
    has_audio = models.BooleanField(default=False)
    audio_file = models.CharField(max_length=255, blank=True, null=True)
    has_diagram = models.BooleanField(default=False)
    diagram_file = models.CharField(max_length=255, blank=True, null=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."


class QueryCache(models.Model):
    """Cache for frequently asked questions"""
    query_hash = models.CharField(max_length=64, unique=True, db_index=True)
    query_text = models.TextField()
    grade = models.IntegerField()
    response = models.TextField()
    retrieval_context = models.TextField(blank=True, null=True)
    
    # Cache metadata
    hit_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['query_hash', 'grade']),
        ]
    
    def __str__(self):
        return f"Cache: {self.query_text[:50]}... (Grade {self.grade})"


class LearningAnalytics(models.Model):
    """Track student learning patterns and performance"""
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='analytics')
    
    # Subject tracking
    subject = models.CharField(max_length=50)  # math, science, social, etc.
    topic = models.CharField(max_length=100)
    
    # Performance metrics
    queries_on_topic = models.IntegerField(default=1)
    understood = models.BooleanField(default=False)  # Did student understand?
    needed_simpler_explanation = models.BooleanField(default=False)
    asked_for_resources = models.BooleanField(default=False)
    
    # Engagement
    follow_up_questions = models.IntegerField(default=0)
    time_spent = models.FloatField(default=0.0)  # minutes
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Learning Analytics'
        indexes = [
            models.Index(fields=['student', 'subject', 'topic']),
        ]
    
    def __str__(self):
        return f"{self.student.name} - {self.subject}/{self.topic}"


class ResourceRecommendation(models.Model):
    """Store recommended learning resources"""
    RESOURCE_TYPE_CHOICES = [
        ('video', 'Video'),
        ('article', 'Article'),
        ('ncert_link', 'NCERT Link'),
        ('practice', 'Practice Problems'),
        ('game', 'Educational Game')
    ]
    
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='recommendations')
    subject = models.CharField(max_length=50)
    topic = models.CharField(max_length=100)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    url = models.URLField()
    description = models.TextField(blank=True)
    
    # Track effectiveness
    clicked = models.BooleanField(default=False)
    found_helpful = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.resource_type}"
