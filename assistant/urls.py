from django.urls import path
from .views import register_view, chat_view, CustomLoginView, logout_view

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('chat/', chat_view, name='chat'),
]
