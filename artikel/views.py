from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.db import models
from django.templatetags.static import static
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from artikel.models import Artikel
import random as py_random
import uuid
import os
import json

# =========================================================
# 🔹 HALAMAN UTAMA ARTIKEL (Web)
# =========================================================
def show_artikel(request):
    latest_artikels = Artikel.objects.order_by('-created_at')[:5]
    popular_artikels = Artikel.objects.order_by('-views')[:9]
    hottest_artikels = Artikel.objects.annotate(
        like_count=models.Count('likes')
    ).order_by('-like_count', '-created_at')[:5]

    recommended_artikels = list(Artikel.objects.all())
    py_random.shuffle(recommended_artikels)
    recommended_artikels = recommended_artikels[:7]

    is_admin = getattr(request.user, 'is_admin', False) if request.user.is_authenticated else False

    return render(request, 'full_artikel.html', {
        'latest_artikels': latest_artikels,
        'recommended_artikels': recommended_artikels,
        'popular_artikels': popular_artikels,
        'hottest_artikels': hottest_artikels,
        'is_admin': is_admin,
    })


# =========================================================
# 🔹 DETAIL ARTIKEL (Web)
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
# 🔹 CREATE ARTIKEL (Web)
# =========================================================
@login_required
@csrf_exempt
def create_artikel(request):
    if not getattr(request.user, 'is_admin', False):
        return HttpResponseForbidden("Kamu tidak memiliki izin untuk membuat artikel.")

    if request.method != "POST":
        return JsonResponse({'status': 'error', 'message': 'Only POST allowed.'}, status=405)

    title = request.POST.get("title", "").strip()
    description = request.POST.get("description", "").strip()
    image = request.POST.get("image", "").strip()

    if not title or not description:
        return JsonResponse({'status': 'error', 'message': 'Judul dan deskripsi wajib diisi.'}, status=400)

    artikel = Artikel.objects.create(title=title, description=description, image=image)
    return JsonResponse({'status': 'success', 'message': 'Artikel berhasil dibuat.', 'id': str(artikel.id)}, status=201)


# =========================================================
# 🔹 CREATE ARTIKEL (Flutter / REST API)
# =========================================================
@csrf_exempt
@require_POST
def create_artikel_flutter(request):
    try:
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        image = request.FILES.get('image')

        if not title or not description:
            return JsonResponse({'status': 'error', 'message': 'Title and description are required.'}, status=400)

        image_path = None
        if image:
            allowed_ext = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
            ext = os.path.splitext(image.name)[1].lower()
            if ext not in allowed_ext:
                return JsonResponse({'status': 'error', 'message': f'Unsupported image format. Allowed: {", ".join(allowed_ext)}.'}, status=400)
            filename = f"artikels/{uuid.uuid4()}{ext}"
            path = default_storage.save(filename, ContentFile(image.read()))
            image_path = path

        artikel = Artikel.objects.create(title=title, description=description, image=image_path)
        return JsonResponse({'status': 'success', 'message': 'Artikel created successfully.', 'id': str(artikel.id)}, status=201)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Internal error: {str(e)}'}, status=500)


# =========================================================
# 🔹 EDIT ARTIKEL (Web)
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
        image = request.POST.get('image', '').strip()

        if not title or not description:
            return JsonResponse({'status': 'error', 'message': 'Judul dan deskripsi wajib diisi.'}, status=400)

        artikel.title = title
        artikel.description = description
        artikel.image = image
        artikel.save()
        return JsonResponse({'status': 'success', 'message': 'Artikel berhasil diperbarui.'})
    return JsonResponse({'status': 'error', 'message': 'Gunakan AJAX POST untuk mengedit.'}, status=405)


# =========================================================
# 🔹 EDIT ARTIKEL (Flutter)
# =========================================================
@login_required
@csrf_exempt
def edit_artikel_flutter(request, artikel_id):
    if not getattr(request.user, 'is_admin', False):
        return HttpResponseForbidden("Hanya admin yang dapat mengedit artikel.")
    
    artikel = get_object_or_404(Artikel, pk=artikel_id)

    if request.method == 'POST':
        artikel.title = request.POST.get('title', artikel.title)
        artikel.description = request.POST.get('description', artikel.description)
        if 'image' in request.FILES:
            artikel.image = request.FILES['image']
        artikel.save()
        return JsonResponse({'status': 'success', 'message': 'Artikel berhasil diperbarui.'})
    return JsonResponse({'status': 'error', 'message': 'Only POST allowed.'}, status=405)


# =========================================================
# 🔹 DELETE ARTIKEL (Web + API)
# =========================================================
@login_required
@csrf_exempt
def delete_artikel(request, id):
    if not getattr(request.user, 'is_admin', False):
        return HttpResponseForbidden("Kamu tidak memiliki izin untuk menghapus artikel ini.")

    artikel = get_object_or_404(Artikel, pk=id)

    if request.method in ['DELETE', 'POST']:
        artikel.delete()
        return JsonResponse({'status': 'success', 'message': 'Artikel berhasil dihapus.'})
    return JsonResponse({'status': 'error', 'message': 'Gunakan method POST atau DELETE.'}, status=405)


# =========================================================
# 🔹 LIKE ARTIKEL (Web + API)
# =========================================================
@login_required
@require_POST
@csrf_exempt
def like_artikel(request, id):
    artikel = get_object_or_404(Artikel, pk=id)
    user = request.user
    liked = False

    if artikel.likes.filter(id=user.id).exists():
        artikel.likes.remove(user)
    else:
        artikel.likes.add(user)
        liked = True

    return JsonResponse({'status': 'success', 'liked': liked, 'total_likes': artikel.total_likes()})


# =========================================================
# 🔹 Rekomendasi Acak (Web + Flutter)
# =========================================================
def get_random_recommendations(request):
    if request.method != "GET":
        return JsonResponse({'error': 'Gunakan method GET.'}, status=405)

    artikels = list(Artikel.objects.all())
    py_random.shuffle(artikels)
    artikels = artikels[:6]

    data = [{
        "id": str(a.id),
        "title": a.title,
        "image": a.image if (a.image and a.image.startswith("http")) else request.build_absolute_uri(a.image.url) if a.image else static('image/no-artikel.png')
    } for a in artikels]

    return JsonResponse({'artikels': data})


# =========================================================
# 🔹 JSON & XML (untuk API Flutter)
# =========================================================
def show_json_all(request):
    data = Artikel.objects.all()
    serialized = serializers.serialize("json", data)
    return HttpResponse(serialized, content_type="application/json")


def show_json_by_id(request, id):
    artikel = get_object_or_404(Artikel, pk=id)
    serialized = serializers.serialize("json", [artikel])
    return HttpResponse(serialized, content_type="application/json")


def show_xml_all(request):
    data = Artikel.objects.all()
    serialized = serializers.serialize("xml", data)
    return HttpResponse(serialized, content_type="application/xml")


def show_xml_by_id(request, id):
    artikel = Artikel.objects.filter(pk=id)
    serialized = serializers.serialize("xml", artikel)
    return HttpResponse(serialized, content_type="application/xml")


# =========================================================
# 🔹 INDEX PAGE (fallback)
# =========================================================
def index(request):
    return render(request, 'full_artikel.html')
