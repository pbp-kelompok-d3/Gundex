from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import WishlistItem
from explore_gunung.models import Gunung # Import model Gunung lagi
import json

# Hanya bisa diakses oleh user yang sudah log in
@login_required(login_url='/login/')
def show_wishlist(request):
    # Ambil semua item wishlist HANYA untuk user yang sedang login
    items = WishlistItem.objects.filter(user=request.user)
    context = {
        'items': items,
        'nama_user': request.user.username,
    }
    # Menghasilkan respons HTML
    return render(request, 'wishlist.html', context)

# Fungsi ini untuk dipanggil oleh AJAX (saat user klik "Add" di hal. Explore)
@login_required(login_url='/login/')
def add_to_wishlist_ajax(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        gunung_id = data.get('gunung_id')
        gunung = get_object_or_404(Gunung, pk=gunung_id)
        
        # Cek apakah sudah ada di wishlist
        if not WishlistItem.objects.filter(user=request.user, gunung=gunung).exists():
            WishlistItem.objects.create(user=request.user, gunung=gunung)
            # Menghasilkan respons JSON
            return JsonResponse({'status': 'success', 'message': 'Berhasil ditambahkan ke wishlist!'})
        else:
            return JsonResponse({'status': 'exists', 'message': 'Gunung ini sudah ada di wishlist.'})
    return JsonResponse({'status': 'failed', 'message': 'Request tidak valid.'}, status=400)

# Fungsi untuk menghapus dari wishlist (via AJAX dari halaman wishlist)
@login_required(login_url='/login/')
def remove_from_wishlist_ajax(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(WishlistItem, pk=item_id, user=request.user) # Pastikan item milik user
        item.delete()
        return JsonResponse({'status': 'success', 'message': 'Berhasil dihapus dari wishlist.'})
    return JsonResponse({'status': 'failed', 'message': 'Request tidak valid.'}, status=400)