from django.urls import path
from .views import (
    create_user, get_users, get_user, update_user, delete_user,
    file_upload, file_history, cleanup_files, get_document,
    user_login, user_logout, chat, getners,
    api_summarize, api_extract_contributions, api_extract_keywords,
    api_generate_qa, api_methodology_insights, api_extract_citations, api_read_aloud,
)

urlpatterns = [
    path('users/', get_users, name='get_users'),
    path('users/create/', create_user, name='create_user'),
    path('users/<int:id>/', get_user, name='get_user'),
    path('users/update/<int:id>/', update_user, name='update_user'),
    path('users/delete/<int:id>/', delete_user, name='delete_user'),
    path('users/upload/', file_upload, name='file_upload'),
    path('users/cleanup/', cleanup_files, name='cleanup_files'),
    path('users/history/', file_history, name='file_history'),
    path('users/document/<int:id>/', get_document, name='get_document'),
    path('users/login/', user_login, name='login'),
    path('users/logout/', user_logout, name='logout'),
    path('users/chat/', chat, name='chat'),
    path('users/ncr/', getners, name='ners'),
    path('users/summarize/', api_summarize, name='api_summarize'),
    path('users/extract-contributions/', api_extract_contributions, name='api_extract_contributions'),
    path('users/extract-keywords/', api_extract_keywords, name='api_extract_keywords'),
    path('users/generate-qa/', api_generate_qa, name='api_generate_qa'),
    path('users/methodology-insights/', api_methodology_insights, name='api_methodology_insights'),
    path('users/extract-citations/', api_extract_citations, name='api_extract_citations'),
    path('users/read-aloud/', api_read_aloud, name='api_read_aloud'),
]