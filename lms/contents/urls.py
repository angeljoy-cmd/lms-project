from django.urls import path
from . import views

app_name = 'contents'  # or whatever your app namespace is

urlpatterns = [
    path('select/', views.select_subj, name='select_subj'),
    path('select_subj/', views.select_subj, name='select_subj'),
    path('content_list/', views.content_list, name='content_list'),
    path('upload_content/', views.upload_content, name='upload_content'),
    path('contents/<int:pk>/', views.edit_content, name='edit_content'),
    path('delete/<int:content_id>/', views.delete_content, name='delete_content'),
    path('view/<int:content_id>/', views.view_content, name='view_content'),
    path('get_students_by_subject/<int:subject_id>/', views.get_students_by_subject, name='get_students_by_subject'),
]
