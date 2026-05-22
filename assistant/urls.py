from django.urls import path
from .views import register_view, chat_view, CustomLoginView, logout_view, delete_chat

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('', chat_view, name='chat_new'),
    path('chat/<int:session_id>/', chat_view, name='chat_detail'),
    path('chat/delete/<int:session_id>/', delete_chat, name='delete_chat'),
]
