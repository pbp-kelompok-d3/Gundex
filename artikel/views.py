from django.shortcuts import render, redirect, reverse , get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from artikel.forms import ArtikelForm
from artikel.models import Artikel
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.contrib import messages
import uuid
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
# Create your views here.
def is_admin(user):
    return user.is_staff or user.is_superuser

def show_artikel(request):
    latest_artikels = Artikel.objects.order_by('-created_at')[:7]
    recommended_artikels = Artikel.objects.all()[:5]
    popular_artikels = Artikel.objects.order_by('-views')[:5]

    return render(request, 'full_artikel.html', {
        'latest_artikels': latest_artikels,
        'recommended_artikels': recommended_artikels,
        'popular_artikels': popular_artikels,
    })

def index(request):
    return render(request, 'full_artikel.html')

def artikel_detail(request, id):
    artikel = get_object_or_404(Artikel, id=id)
    return render(request, 'artikel_detail.html', {'artikel': artikel}) 

def create_artikel(request):
    if request.method != "POST":
        return JsonResponse({
            "status": "error",
            "message": "Invalid request method. Only POST allowed."
        }, status=405)

    try:
        # 1️⃣ Ambil data dari request
        title = request.POST.get("title", "")
        description = request.POST.get("description", "")
        image = request.FILES.get("image")

        # 2️⃣ Validasi input
        if not title or not description:
            return JsonResponse({
                "status": "error",
                "message": "Title and description are required."
            }, status=400)

        # 3️⃣ Simpan data baru ke database
        new_artikel = Artikel.objects.create(
            title=title,
            description=description,
            image=image
        )

        # 4️⃣ Kirim respons sukses dalam format JSON
        return JsonResponse({
            "status": "success",
            "message": "Artikel created successfully!",
            "artikel_id": new_artikel.id
        }, status=201)

    except Exception as e:
        # 5️⃣ Kalau error, kirim JSON error message
        return JsonResponse({
            "status": "error",
            "message": f"Internal server error: {str(e)}"
        }, status=500)

def delete_artikel(request, id):
    if not request.user.is_staff:
        return HttpResponseForbidden("Kamu tidak memiliki izin untuk menghapus artikel ini.")
    try:
        artikel = get_object_or_404(Artikel, pk=id)

        # Jika request dari AJAX (DELETE)
        if request.method == 'DELETE':
            artikel.delete()
            return HttpResponse(status=204)  # No Content

        # Jika request dari form biasa (POST)
        elif request.method == 'POST':
            artikel.delete()
            return HttpResponseRedirect(reverse('artikel:show_artikel'))

        else:
            return JsonResponse(
                {'error': 'Invalid HTTP method. Use POST or DELETE.'},
                status=405
            )

    except Exception as e:
        print(f"Error deleting artikel: {e}")
        return JsonResponse(
            {'error': 'An error occurred while deleting the artikel.'},
            status=500
        )
    
def edit_artikel(request, id):
    if not request.user.is_staff:
        return HttpResponseForbidden("Kamu tidak memiliki izin untuk mengedit artikel ini.")

    artikel = get_object_or_404(Artikel, pk=id)

    if request.method == 'POST':
        title = request.POST.get('title', '')
        description = request.POST.get('description', '')
        image = request.FILES.get('image')

        if not title or not description:
            messages.error(request, 'Please fill in all fields first.')
        else:
            artikel.title = title
            artikel.description = description
            if image:
                artikel.image = image
            artikel.save()
            messages.success(request, 'Artikel successfully updated.')
            return redirect('artikel:full_artikel')

    return render(request, 'edit_artikel.html', {'artikel': artikel})

def get_more_artikels(request):
    """Return JSON data for lazy loading / infinite scroll"""
    if request.method == "GET":
        start = int(request.GET.get("start", 0))
        limit = int(request.GET.get("limit", 5))
        artikels = Artikel.objects.all().order_by('-id')[start:start+limit]

        data = [
            {
                "id": artikel.id,
                "title": artikel.title,
                "description": artikel.description[:100],
                "thumbnail": artikel.image.url if artikel.image else "",
            }
            for artikel in artikels
        ]

        return JsonResponse({"artikels": data})