from django.urls import path
from .views import *

urlpatterns = [
    # 🔹 USER APIs
    path('users/', get_users),
    path('users/create/', create_user),
    path('users/<int:id>/', get_user),
    path('users/update/<int:id>/', update_user),
    path('users/delete/<int:id>/', delete_user),

    # 🔹 AUTH
    path('users/login/', user_login),
    path('users/logout/', user_logout),

    # 🔹 FILE
    path('users/upload/', file_upload),
    path('users/history/', file_history),
    path('users/document/<int:id>/', get_document),
    path('users/cleanup/', cleanup_files),

    # 🔹 AI FEATURES
    path('users/summarize/', api_summarize),
    path('users/extract-contributions/', api_extract_contributions),
    path('users/extract-keywords/', api_extract_keywords),
    path('users/generate-qa/', api_generate_qa),
    path('users/methodology-insights/', api_methodology_insights),
    path('users/extract-citations/', api_extract_citations),
    path('users/read-aloud/', api_read_aloud),

    # 🔹 EXTRA
    path('users/chat/', chat),
    path('users/ncr/', getners),
    path('users/protected/', protected_view),
]