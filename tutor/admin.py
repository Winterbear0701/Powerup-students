from django.contrib import admin
from .models import StudentProfile, Conversation, Message, QueryCache, LearningAnalytics, ResourceRecommendation


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['name', 'grade', 'current_difficulty_level', 'total_queries', 'created_at']
    list_filter = ['grade', 'current_difficulty_level', 'preferred_learning_style']
    search_fields = ['name', 'user__username']


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'student', 'started_at', 'is_active']
    list_filter = ['is_active', 'started_at']
    search_fields = ['session_id', 'student__name']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'role', 'timestamp', 'has_audio', 'has_diagram']
    list_filter = ['role', 'has_audio', 'has_diagram', 'timestamp']
    search_fields = ['content']


@admin.register(QueryCache)
class QueryCacheAdmin(admin.ModelAdmin):
    list_display = ['query_text', 'grade', 'hit_count', 'last_accessed']
    list_filter = ['grade', 'created_at']
    search_fields = ['query_text']


@admin.register(LearningAnalytics)
class LearningAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'topic', 'understood', 'timestamp']
    list_filter = ['subject', 'understood', 'timestamp']
    search_fields = ['student__name', 'topic']


@admin.register(ResourceRecommendation)
class ResourceRecommendationAdmin(admin.ModelAdmin):
    list_display = ['student', 'title', 'resource_type', 'clicked', 'found_helpful']
    list_filter = ['resource_type', 'clicked', 'found_helpful']
    search_fields = ['title', 'student__name']
