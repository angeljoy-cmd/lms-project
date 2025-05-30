# --- users/views.py --- (Remember, you're putting this in accounts/views.py now)
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserLoginForm
from django.contrib import messages


def user_login(request):
    """
    Handles user login.
    If the request is POST, it attempts to authenticate the user.
    If successful, it logs the user in and redirects to the dashboard.
    """
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('select_subj') # Changed from 'dashboard' to 'select_subj'
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    return render(request, 'registration/login.html', {'form': form})

@login_required # Decorator to ensure only logged-in users can access this view
def dashboard(request):
    """
    A simple dashboard view for logged-in users.
    """
    return render(request, 'dashboard.html')

def user_logout(request):
    """
    Logs out the current user and redirects to the login page.
    """
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')