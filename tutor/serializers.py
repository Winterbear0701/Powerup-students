"""
Django REST Framework Serializers
"""
from rest_framework import serializers
from .models import StudentProfile, Conversation, Message, LearningAnalytics, ResourceRecommendation
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class StudentProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = StudentProfile
        fields = '__all__'
        read_only_fields = ['total_queries', 'successful_interactions', 'struggle_count',
                           'current_difficulty_level', 'created_at', 'updated_at']


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'
        read_only_fields = ['timestamp']


class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    student = StudentProfileSerializer(read_only=True)
    
    class Meta:
        model = Conversation
        fields = '__all__'
        read_only_fields = ['started_at', 'ended_at']


class LearningAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningAnalytics
        fields = '__all__'
        read_only_fields = ['timestamp']


class ResourceRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourceRecommendation
        fields = '__all__'
        read_only_fields = ['created_at']


class ChatQuerySerializer(serializers.Serializer):
    """Serializer for chat query requests"""
    query = serializers.CharField(required=True)
    session_id = serializers.CharField(required=False)
    include_audio = serializers.BooleanField(default=False)
    include_diagram = serializers.BooleanField(default=True)


class VoiceQuerySerializer(serializers.Serializer):
    """Serializer for voice query requests"""
    audio_file = serializers.FileField(required=True)
    session_id = serializers.CharField(required=False)
