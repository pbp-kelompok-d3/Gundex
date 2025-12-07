from random import random
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, JsonResponse
import requests
from artikel.models import Artikel
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import random as py_random
from django.views.decorators.http import require_POST
from django.db import models
from django.templatetags.static import static
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json
import os
from django.core import serializers
from django.contrib import messages
from django.core.paginator import Paginator

# =========================================================
# 🔹 HALAMAN UTAMA ARTIKEL
# =========================================================
def show_artikel(request):
    latest_artikels = Artikel.objects.order_by('-created_at')[:5]
    popular_artikels = Artikel.objects.order_by('-views')[:9]
    hottest_artikels = Artikel.objects.annotate(like_count=models.Count('likes')).order_by('-like_count', '-created_at')[:5]
    recommended_artikels = list(Artikel.objects.all())
    py_random.shuffle(recommended_artikels)
    recommended_artikels = recommended_artikels[:7]

    is_admin = False
    if request.user.is_authenticated:
        # cek jika pakai userprofile atau fallback ke is_staff bawaan
        if hasattr(request.user, 'is_admin'):
            is_admin = request.user.is_admin
    return render(request, 'full_artikel.html', {
        'latest_artikels': latest_artikels,
        'recommended_artikels': recommended_artikels,
        'popular_artikels': popular_artikels,
        'hottest_artikels': hottest_artikels,
        'is_admin': is_admin,
    })


# =========================================================
# 🔹 HALAMAN INDEX ARTIKEL
# =========================================================
def index(request):
    return render(request, 'full_artikel.html')


# =========================================================
# 🔹 DETAIL ARTIKEL
# =========================================================
@login_required
def artikel_detail(request, id):
    artikel = get_object_or_404(Artikel, id=id)
    artikel.views += 1
    artikel.save(update_fields=['views'])
    return render(request, 'artikel_detail.html', {
        'artikel': artikel,
        'is_admin': getattr(request.user, "is_admin", False),
    })


# =========================================================
# 🔹 CREATE ARTIKEL (Admin Only)
# =========================================================
@login_required
@csrf_exempt
def create_artikel(request):
    if not request.user.is_admin:
        return HttpResponseForbidden("Kamu tidak memiliki izin untuk membuat artikel.")

    if request.method != "POST":
        return JsonResponse({
            "status": "error",
            "message": "Invalid request method. Only POST allowed."
        }, status=405)

    try:
        title = request.POST.get("title", "")
        description = request.POST.get("description", "")
        image = request.POST.get("image")

        if not title or not description:
            return JsonResponse({
                "status": "error",
                "message": "Judul dan deskripsi wajib diisi."
            }, status=400)

        new_artikel = Artikel.objects.create(
            title=title,
            description=description,
            image=image
        )

        return JsonResponse({
            "status": "success",
            "message": "Artikel berhasil dibuat!",
            "artikel_id": new_artikel.id
        }, status=201)

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": f"Terjadi kesalahan internal: {str(e)}"
        }, status=500)
@login_required
@csrf_exempt
def create_artikel_flutter(request):
    try:
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        image = request.FILES.get('image')

        # Validasi input
        if not title or not description:
            return JsonResponse({
                'status': 'error',
                'message': 'Title and description are required.'
            }, status=400)

        if image:
            # Validasi format gambar
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
            file_extension = os.path.splitext(image.name)[1].lower()

            if file_extension not in allowed_extensions:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Unsupported image format. Allowed formats are: {", ".join(allowed_extensions)}.'
                }, status=400)

            # Buat path penyimpanan unik
            filename = f"artikels/{uuid.uuid4()}{file_extension}"

            # Simpan file
            path = default_storage.save(filename, ContentFile(image.read()))
            image_path = path
        else:
            image_path = None

        # Buat artikel baru
        new_artikel = Artikel(
            title=title,
            description=description,
            image=image_path  # Simpan path gambar
        )
        new_artikel.save()

        return JsonResponse({
            'status': 'success',
            'message': 'Artikel created successfully.',
            'artikel_id': new_artikel.id
        }, status=201)

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'An error occurred: {str(e)}'
        }, status=500)

# =========================================================
# 🔹 EDIT ARTIKEL (Admin Only + AJAX)
# =========================================================
@login_required
@csrf_exempt
def edit_artikel(request, id):
    if not getattr(request.user, 'is_admin', False):
        return HttpResponseForbidden("Kamu tidak memiliki izin untuk mengedit artikel ini.")

    artikel = get_object_or_404(Artikel, pk=id)

    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        image = request.POST.get('image', '').strip()  # URL gambar

        if not title or not description:
            return JsonResponse({'status': 'error', 'message': 'Judul dan deskripsi wajib diisi.'}, status=400)

        artikel.title = title
        artikel.description = description
        artikel.image = image
        artikel.save()
        return JsonResponse({'status': 'success', 'message': 'Artikel berhasil diperbarui!'})

    return JsonResponse({'status': 'error', 'message': 'Gunakan AJAX POST untuk mengedit.'}, status=405)
@login_required
@csrf_exempt
def edit_artikel_flutter(request, id):
    if request.method == 'POST':
        artikel = get_object_or_404(Artikel, pk=id)
        
        # Update title dan description
        artikel.title = request.POST.get('title')
        artikel.description = request.POST.get('description')
        
        # Update gambar jika ada
        if 'image' in request.FILES:
            artikel.image = request.FILES['image']
        
        artikel.save()
        
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error'}, status=400)
# =========================================================
# 🔹 DELETE ARTIKEL (Admin Only + AJAX)
# =========================================================
@login_required
@csrf_exempt
def delete_artikel(request, id):
    if not request.user.is_admin:
        return HttpResponseForbidden("Kamu tidak memiliki izin untuk menghapus artikel ini.")

    artikel = get_object_or_404(Artikel, pk=id)
    try:
        # DELETE via AJAX
        if request.method == 'DELETE' or (request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest'):
            artikel.delete()
            return JsonResponse({'status': 'success', 'message': 'Artikel berhasil dihapus.'}, status=200)

        # DELETE via POST form biasa
        elif request.method == 'POST':
            artikel.delete()
            return HttpResponseRedirect(reverse('artikel:show_artikel'))

        else:
            return JsonResponse({'error': 'Gunakan method POST atau DELETE.'}, status=405)

    except Exception as e:
        print(f"Error deleting artikel: {e}")
        return JsonResponse({'error': f'Kesalahan internal: {str(e)}'}, status=500)

@login_required
@csrf_exempt
def delete_artikel_flutter(request, id):
    if request.method != "DELETE":
        return JsonResponse({"error": "DELETE required"}, status=405)

    artikel = get_object_or_404(Artikel, pk=id)
    artikel.delete()

    return JsonResponse({"status": "success"})
# =========================================================
# 🔹 EDIT MODAL RENDER (untuk AJAX load)
# =========================================================
@login_required
def edit_artikel_modal(request, id):
    if not request.user.is_admin:
        return HttpResponseForbidden("Kamu bukan admin.")
    artikel = get_object_or_404(Artikel, pk=id)
    return render(request, "edit_artikel.html", {"artikel": artikel})


# =========================================================
# 🔹 REKOMENDASI ACAK (AJAX refresh)
# =========================================================
def get_random_recommendations(request):
    """Return new random recommended artikels (AJAX refresh)"""
    if request.method == "GET":
        artikels = list(Artikel.objects.all())
        py_random.shuffle(artikels)
        artikels = artikels[:6]  # ambil 6 acak
        data = [
            {
                "id": str(a.id),
                "title": a.title,
                "image": a.image or static('image/no-artikel.png'), 
            }
            for a in artikels
        ]
        return JsonResponse({"artikels": data})
    return JsonResponse({"error": "Gunakan method GET"}, status=405)

@login_required
@require_POST
@csrf_exempt
def like_artikel(request, id):
    artikel = get_object_or_404(Artikel, pk=id)
    user = request.user

    if artikel.likes.filter(id=user.id).exists():
        artikel.likes.remove(user)
        liked = False
    else:
        artikel.likes.add(user)
        liked = True

    return JsonResponse({
        "status": "success",
        "liked": liked,
        "total_likes": artikel.total_likes()
    })



def show_xml(request):
   data = Artikel.objects.all()
   return HttpResponse(serializers.serialize("xml", data), content_type="application/xml")

# menampilkan artikel berdasarkan id dalam format JSON
def show_json(request):
    artikels = Artikel.objects.all().order_by("-created_at")

    data = []
    for a in artikels:
        # absolute image url
        image_url = None
        if a.image:
            # URLField → string (langsung absolut jika sudah absolut)
            if a.image.startswith("http"):
                image_url = a.image
            else:
                image_url = request.build_absolute_uri(a.image)

        data.append({
            "id": str(a.id),
            "title": a.title,
            "description": a.description,
            "image": image_url,
            "views": a.views,
            "likes": a.total_likes(),
            "created_at": a.created_at.isoformat(),
        })

    return JsonResponse(data, safe=False)

# menampilkan artikel berdasarkan id dalam format JSON
def show_xml_by_id(request, id):
    data = Artikel.objects.filter(pk=id)
    return HttpResponse(serializers.serialize("xml", data), content_type="application/xml")

# menampilkan artikel berdasarkan id dalam format JSON
def show_json_by_id(request, id):
    try:
        a = Artikel.objects.get(pk=id)

        image_url = None
        if a.image:
            if a.image.startswith("http"):
                image_url = a.image
            else:
                image_url = request.build_absolute_uri(a.image)

        data = {
            "id": str(a.id),
            "title": a.title,
            "description": a.description,
            "image": image_url,
            "views": a.views,
            "likes": a.total_likes(),
            "created_at": a.created_at.isoformat(),
        }

        return JsonResponse(data)

    except Artikel.DoesNotExist:
        return JsonResponse({"error": "Not found"}, status=404)
    
def proxy_image(request):
    url = request.GET.get("url")
    if not url:
        return HttpResponse("Missing URL", status=400)

    r = requests.get(url, stream=True)
    return HttpResponse(r.content, content_type=r.headers["Content-Type"])