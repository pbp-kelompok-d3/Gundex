from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.views.decorators.cache import never_cache
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegisterForm, EditProfileForm 
from .models import UserProfile
import datetime
import json

@csrf_protect
@never_cache
def register(request):
    if request.method == 'POST':
        # Check if it's an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            form = RegisterForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.set_password(form.cleaned_data['password'])
                # All users are regular hikers by default
                user.is_admin = False
                user.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Registration successful! You can now login.',
                    'redirect_url': reverse('userprofile:login')
                })
            else:
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                })
        else:
            # Handle regular form submission
            form = RegisterForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.set_password(form.cleaned_data['password'])
                # All users are regular hikers by default
                user.is_admin = False
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
        return redirect('main:show_main')
    
    if request.method == 'POST':
        # Check if it's an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            form = AuthenticationForm(data=request.POST)
            if form.is_valid():
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                user = authenticate(request, username=username, password=password)
                
                if user is not None:
                    auth_login(request, user)
                    
                    return JsonResponse({
                        'success': True,
                        'message': f'Welcome back, {user.username}!',
                        'redirect_url': reverse('main:show_main'),
                        'user_data': {
                            'username': user.username,
                            'is_admin': user.is_admin,
                            'first_name': user.first_name,
                            'last_name': user.last_name
                        }
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'errors': {'__all__': ['Invalid username or password.']}
                    })
            else:
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                })
        else:
            # Handle regular form submission
            form = AuthenticationForm(data=request.POST)
            if form.is_valid():
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                user = authenticate(request, username=username, password=password)
                
                if user is not None:
                    auth_login(request, user)
                    
                    # Set secure cookies
                    response = HttpResponseRedirect(reverse('main:show_main'))
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
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        username = request.user.username
        auth_logout(request)
        
        return JsonResponse({
            'success': True,
            'message': f'Goodbye, {username}! You have been logged out.',
            'redirect_url': reverse('main:show_main')
        })
    else:
        username = request.user.username
        auth_logout(request)
        
        # Clear cookies and redirect
        response = redirect('main:show_main')
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


# ============ Flutter Endpoints ============

@csrf_exempt
def flutter_login(request):
    """Login endpoint specifically for Flutter mobile app"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            return JsonResponse({
                "status": False,
                "message": "Username and password are required."
            }, status=400)
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
            return JsonResponse({
                "username": user.username,
                "status": True,
                "message": "Login successful!",
                "user_data": {
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "bio": user.bio if user.bio else "",
                    "is_admin": user.is_admin
                }
            }, status=200)
        else:
            return JsonResponse({
                "status": False,
                "message": "Invalid username or password."
            }, status=401)
    
    return JsonResponse({
        "status": False,
        "message": "Invalid request method."
    }, status=400)

@csrf_exempt
def flutter_register(request):
    """Register endpoint specifically for Flutter mobile app"""
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        password1 = data.get('password1')
        password2 = data.get('password2')
        bio = data.get('bio', '')

        # Validation
        if password1 != password2:
            return JsonResponse({
                "status": False,
                "message": "Passwords do not match."
            }, status=400)
        
        if UserProfile.objects.filter(username=username).exists():
            return JsonResponse({
                "status": False,
                "message": "Username already exists."
            }, status=400)
        
        if UserProfile.objects.filter(email=email).exists():
            return JsonResponse({
                "status": False,
                "message": "Email already exists."
            }, status=400)
        
        # Create user
        try:
            user = UserProfile.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name,
                bio=bio,
                is_admin=False
            )
            
            return JsonResponse({
                "username": user.username,
                "status": 'success',
                "message": "User created successfully!"
            }, status=200)
        except Exception as e:
            return JsonResponse({
                "status": False,
                "message": f"Registration failed: {str(e)}"
            }, status=400)
    
    return JsonResponse({
        "status": False,
        "message": "Invalid request method."
    }, status=400)

@csrf_exempt
def flutter_logout(request):
    """Logout endpoint specifically for Flutter mobile app"""
    username = request.user.username if request.user.is_authenticated else "Guest"
    try:
        auth_logout(request)
        return JsonResponse({
            "username": username,
            "status": True,
            "message": "Logged out successfully!"
        }, status=200)
    except Exception as e:
        return JsonResponse({
            "status": False,
            "message": f"Logout failed: {str(e)}"
        }, status=401)

@csrf_exempt
def get_user_profile_flutter(request):
    """Get user profile for Flutter mobile app"""
    if not request.user.is_authenticated:
        return JsonResponse({
            "status": False,
            "message": "Not authenticated"
        }, status=401)
    
    user = request.user
    return JsonResponse({
        "status": True,
        "user_data": {
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "bio": user.bio if user.bio else "",
            "is_admin": user.is_admin
        }
    }, status=200)

@csrf_exempt
def update_profile_flutter(request):
    """Update user profile for Flutter mobile app"""
    if not request.user.is_authenticated:
        return JsonResponse({
            "status": False,
            "message": "Not authenticated"
        }, status=401)
    
    if request.method == 'POST':
        data = json.loads(request.body)
        user = request.user
        
        try:
            user.first_name = data.get('first_name', user.first_name)
            user.last_name = data.get('last_name', user.last_name)
            user.bio = data.get('bio', user.bio)
            user.save()
            
            return JsonResponse({
                "status": True,
                "message": "Profile updated successfully!",
                "user_data": {
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "bio": user.bio,
                    "is_admin": user.is_admin
                }
            }, status=200)
        except Exception as e:
            return JsonResponse({
                "status": False,
                "message": f"Update failed: {str(e)}"
            }, status=400)
    
    return JsonResponse({
        "status": False,
        "message": "Invalid request method."
    }, status=400)