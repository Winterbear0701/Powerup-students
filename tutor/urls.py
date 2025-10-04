"""
URL configuration for tutor app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for viewsets
router = DefaultRouter()
router.register(r'profiles', views.StudentProfileViewSet, basename='profile')
router.register(r'conversations', views.ConversationViewSet, basename='conversation')

app_name = 'tutor'

urlpatterns = [
    # HTML views
    path('', views.index, name='index'),
    path('chat/', views.chat_interface, name='chat'),
    
    # API endpoints
    path('api/', include(router.urls)),
    path('api/chat/', views.chat_query, name='chat_query'),
    path('api/voice/', views.voice_query, name='voice_query'),
    path('api/profile/setup/', views.setup_profile, name='setup_profile'),
    path('api/feedback/', views.feedback, name='feedback'),
]
