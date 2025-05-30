# accounts/urls.py
from django.urls import path, include # Make sure to import include
from django.contrib.auth import views as auth_views

app_name = 'accounts'

urlpatterns = [
    # Login URL
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    # Logout URL
    path('logout/', auth_views.LogoutView.as_view(next_page='accounts:login'), name='logout'),

    # Add all Django's default auth URLs here, but without the 'accounts/' prefix
    # because this file IS already under 'accounts/' namespace in lms/urls.py
    path('', include('django.contrib.auth.urls')), # <--- ADD THIS LINE

    # You can keep other specific account-related URLs here too:
    # path('profile/', views.profile_view, name='profile'),
]