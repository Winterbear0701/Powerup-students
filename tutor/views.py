from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, FileResponse
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.views import APIView
import uuid
import os
import logging

from .models import StudentProfile, Conversation, Message, LearningAnalytics, ResourceRecommendation
from .serializers import (
    StudentProfileSerializer, ConversationSerializer, MessageSerializer,
    LearningAnalyticsSerializer, ChatQuerySerializer, VoiceQuerySerializer
)
from .services.tutor_service import get_tutor_service

logger = logging.getLogger(__name__)


# ============ HTML Views ============

def index(request):
    """Main landing page"""
    return render(request, 'tutor/index.html')


def chat_interface(request):
    """Chat interface page"""
    return render(request, 'tutor/chat.html')


# ============ API Views ============

class StudentProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for student profiles"""
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer
    
    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """Get analytics for a student"""
        student = self.get_object()
        analytics = LearningAnalytics.objects.filter(student=student).order_by('-timestamp')[:20]
        serializer = LearningAnalyticsSerializer(analytics, many=True)
        return Response(serializer.data)


class ConversationViewSet(viewsets.ModelViewSet):
    """ViewSet for conversations"""
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    
    def get_queryset(self):
        """Filter conversations by student if provided"""
        queryset = Conversation.objects.all()
        student_id = self.request.query_params.get('student_id')
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        return queryset.order_by('-started_at')


@api_view(['POST'])
def chat_query(request):
    """
    Handle chat query
    POST /api/chat/
    Body: {
        "query": "What is photosynthesis?",
        "session_id": "optional-session-id",
        "include_audio": false,
        "include_diagram": true
    }
    """
    try:
        serializer = ChatQuerySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Get or create student profile from session
        student_profile = get_or_create_student_from_session(request)
        if not student_profile:
            return Response(
                {'error': 'Please set up your profile first'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or create conversation
        session_id = serializer.validated_data.get('session_id') or str(uuid.uuid4())
        conversation, created = Conversation.objects.get_or_create(
            session_id=session_id,
            student=student_profile,
            defaults={'is_active': True}
        )
        
        # Get conversation history
        history_messages = Message.objects.filter(
            conversation=conversation
        ).order_by('timestamp')[:10]
        
        conversation_history = []
        for msg in history_messages:
            if msg.role == 'user':
                conversation_history.append({
                    'user': msg.content,
                    'bot': ''
                })
            elif msg.role == 'assistant' and conversation_history:
                conversation_history[-1]['bot'] = msg.content
        
        # Process query
        tutor_service = get_tutor_service()
        result = tutor_service.process_query(
            query=serializer.validated_data['query'],
            student_profile={
                'name': student_profile.name,
                'grade': student_profile.grade,
                'difficulty_level': student_profile.current_difficulty_level,
                'struggle_count': student_profile.struggle_count
            },
            conversation_history=conversation_history,
            include_audio=serializer.validated_data.get('include_audio', False),
            include_diagram=serializer.validated_data.get('include_diagram', True)
        )
        
        # Save user message
        user_message = Message.objects.create(
            conversation=conversation,
            role='user',
            content=serializer.validated_data['query']
        )
        
        # Save assistant response
        assistant_message = Message.objects.create(
            conversation=conversation,
            role='assistant',
            content=result['response'],
            retrieval_context=str(result.get('sources', [])),
            llm_model_used=result['metadata'].get('llm', {}).get('model', 'unknown'),
            response_time=result['processing_time'],
            has_audio=bool(result.get('audio_file')),
            audio_file=result.get('audio_file'),
            has_diagram=bool(result.get('diagram_file')),
            diagram_file=result.get('diagram_file')
        )
        
        # Update student stats
        student_profile.total_queries += 1
        student_profile.save()
        
        # Prepare response
        response_data = {
            'response': result['response'],
            'session_id': session_id,
            'message_id': assistant_message.id,
            'sources': result['sources'],
            'suggestions': result.get('suggestions', []),
            'resource_recommendations': result.get('resource_recommendations', []),
            'processing_time': result['processing_time'],
            'has_audio': bool(result.get('audio_file')),
            'audio_url': f"/api/media/{os.path.basename(result['audio_file'])}" if result.get('audio_file') else None,
            'has_diagram': bool(result.get('diagram_file')),
            'diagram_url': f"/api/media/{os.path.basename(result['diagram_file'])}" if result.get('diagram_file') else None
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in chat_query: {e}", exc_info=True)
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def voice_query(request):
    """
    Handle voice query (speech-to-text + chat)
    POST /api/voice/
    Body: multipart/form-data with audio_file
    """
    try:
        serializer = VoiceQuerySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Save uploaded audio temporarily
        audio_file = serializer.validated_data['audio_file']
        temp_path = f"/tmp/{uuid.uuid4()}.wav"
        with open(temp_path, 'wb+') as destination:
            for chunk in audio_file.chunks():
                destination.write(chunk)
        
        # Transcribe audio
        tutor_service = get_tutor_service()
        transcribed_text = tutor_service.transcribe_voice_query(temp_path)
        
        # Clean up temp file
        os.remove(temp_path)
        
        if not transcribed_text:
            return Response(
                {'error': 'Could not transcribe audio'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Process as normal chat query
        request.data['query'] = transcribed_text
        return chat_query(request)
        
    except Exception as e:
        logger.error(f"Error in voice_query: {e}", exc_info=True)
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def setup_profile(request):
    """
    Setup or update student profile
    POST /api/profile/setup/
    Body: {
        "name": "John",
        "age": 12,
        "grade": 7,
        "preferred_learning_style": "visual"
    }
    """
    try:
        # Create or update student profile
        user = request.user if request.user.is_authenticated else None
        
        if not user:
            # Create anonymous user or use session
            from django.contrib.auth.models import User
            username = f"student_{uuid.uuid4().hex[:8]}"
            user = User.objects.create_user(username=username)
            request.session['user_id'] = user.id
        
        profile, created = StudentProfile.objects.get_or_create(
            user=user,
            defaults={
                'name': request.data.get('name', 'Student'),
                'age': request.data.get('age'),
                'grade': request.data.get('grade', 7),
                'preferred_learning_style': request.data.get('preferred_learning_style', 'mixed')
            }
        )
        
        if not created:
            # Update existing profile
            profile.name = request.data.get('name', profile.name)
            profile.age = request.data.get('age', profile.age)
            profile.grade = request.data.get('grade', profile.grade)
            profile.preferred_learning_style = request.data.get('preferred_learning_style', profile.preferred_learning_style)
            profile.save()
        
        serializer = StudentProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in setup_profile: {e}", exc_info=True)
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def feedback(request):
    """
    Submit feedback on a response
    POST /api/feedback/
    Body: {
        "message_id": 123,
        "understood": true,
        "needed_simpler": false
    }
    """
    try:
        message_id = request.data.get('message_id')
        understood = request.data.get('understood', False)
        needed_simpler = request.data.get('needed_simpler', False)
        
        message = get_object_or_404(Message, id=message_id)
        conversation = message.conversation
        student = conversation.student
        
        # Update student difficulty level
        student.adjust_difficulty(success=understood)
        
        # Create learning analytics entry
        LearningAnalytics.objects.create(
            student=student,
            subject='general',  # Should be detected from message
            topic=message.content[:100],
            understood=understood,
            needed_simpler_explanation=needed_simpler
        )
        
        return Response({'status': 'Feedback recorded'}, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in feedback: {e}", exc_info=True)
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ============ Helper Functions ============

def get_or_create_student_from_session(request):
    """Get or create student profile from session"""
    user_id = request.session.get('user_id')
    
    if not user_id:
        return None
    
    try:
        from django.contrib.auth.models import User
        user = User.objects.get(id=user_id)
        profile = StudentProfile.objects.get(user=user)
        return profile
    except:
        return None
