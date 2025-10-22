from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegisterForm, EditProfileForm 
from .models import UserProfile
import datetime

@csrf_protect
@never_cache
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_admin = form.cleaned_data.get('register_as_admin', False)
            user.save()
            
            messages.success(request, 'Registration successful! You can now login.')
            
            # Set cookie to remember registration success
            response = redirect('userprofile:login')
            response.set_cookie('registration_success', 'true', max_age=300)  # 5 minutes
            return response
    else:
        form = RegisterForm()
    
    return render(request, 'register.html', {'form': form})

@csrf_protect
@never_cache
def login_view(request):
    if request.user.is_authenticated:
        return redirect('userprofile:edit_profile')
    
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                auth_login(request, user)
                
                # Set secure cookies
                response = HttpResponseRedirect(reverse('userprofile:edit_profile'))
                response.set_cookie('last_login', 
                                  datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                  max_age=86400,  # 24 hours
                                  secure=True,
                                  httponly=True,
                                  samesite='Lax')
                
                messages.success(request, f'Welcome back, {user.username}!')
                return response
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    # Check for registration success cookie
    registration_success = request.COOKIES.get('registration_success')
    context = {
        'form': form,
        'registration_success': registration_success
    }
    
    return render(request, 'login.html', context)

@login_required
def logout_view(request):
    username = request.user.username
    auth_logout(request)
    
    # Clear cookies and redirect
    response = redirect('userprofile:login')
    response.delete_cookie('last_login')
    response.delete_cookie('registration_success')
    
    messages.success(request, f'Goodbye, {username}! You have been logged out.')
    return response

@login_required
@csrf_protect
@never_cache
def edit_profile(request):
    user = request.user
    last_login_cookie = request.COOKIES.get('last_login')
    
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=user, user=user)
        if form.is_valid():
            updated_user = form.save()
            
            messages.success(request, 'Profile updated successfully!')
            return redirect('userprofile:edit_profile')
    else:
        form = EditProfileForm(instance=user, user=user)
    
    context = {
        'form': form,
        'user': user,
        'last_login': last_login_cookie,
        'is_admin': user.is_admin,
    }
    
    return render(request, 'edit_profile.html', context)