"""
URL configuration for tutor app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, auth_views, admin_views

# Create router for viewsets
router = DefaultRouter()
router.register(r'profiles', views.StudentProfileViewSet, basename='profile')
router.register(r'conversations', views.ConversationViewSet, basename='conversation')

app_name = 'tutor'

urlpatterns = [
    # HTML views
    path('', views.index, name='index'),
    path('dashboard/', views.student_dashboard, name='dashboard'),
    path('chat/', views.chat_interface, name='chat'),
    path('mcq/', views.mcq_practice, name='mcq'),

    # Authentication views
    path('login/', auth_views.login_view, name='login'),
    path('register/', auth_views.register_view, name='register'),
    path('logout/', auth_views.logout_view, name='logout'),
    path('profile/', auth_views.profile_view, name='profile'),

    # Admin views
    path('admin/dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('admin/students/', admin_views.admin_students, name='admin_students'),
    path('admin/conversations/', admin_views.admin_conversations, name='admin_conversations'),
    path('admin/analytics/', admin_views.admin_analytics, name='admin_analytics'),
    path('admin/settings/', admin_views.admin_settings, name='admin_settings'),

    # API endpoints
    path('api/', include(router.urls)),
    path('api/chat/', views.chat_query, name='chat_query'),
    path('api/voice/', views.voice_query, name='voice_query'),
    path('api/profile/setup/', views.setup_profile, name='setup_profile'),
    path('api/feedback/', views.feedback, name='feedback'),
    path('api/profile/update-model/', auth_views.update_model_selection, name='update_model'),
]
