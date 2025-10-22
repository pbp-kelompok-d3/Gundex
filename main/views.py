from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required
def show_main(request):
    context = {
        'npm' : '240123456',
        'name': 'Haru Urara',
        'class': 'PBP A'
    }

    return render(request, "main.html", context)

def redirect_to_login(request):
    """Redirect root URL to login page"""
    return redirect('userprofile:login')