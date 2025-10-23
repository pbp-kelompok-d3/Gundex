from random import random
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, JsonResponse
from artikel.models import Artikel
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import random as py_random
from django.views.decorators.http import require_POST
from django.db import models

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
                "image": a.image if a.image else "",
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