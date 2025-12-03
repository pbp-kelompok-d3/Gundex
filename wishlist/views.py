from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .models import WishlistItem
from explore_gunung.models import Gunung
import json

# Hanya bisa diakses oleh user yang sudah log in
@login_required(login_url=reverse_lazy('userprofile:login'))
def show_wishlist(request):
    # Ambil semua item wishlist HANYA untuk user yang sedang login
    items = WishlistItem.objects.filter(user=request.user).select_related('gunung')
    context = {
        'items': items,
        'nama_user': request.user.username,
    }
    # Menghasilkan respons HTML
    return render(request, 'wishlist.html', context)

# Endpoint JSON untuk mendapatkan wishlist user (dipanggil dari frontend)
@login_required(login_url=reverse_lazy('userprofile:login'))
def get_wishlist_json(request):
    """Return wishlist user dalam format JSON untuk AJAX"""
    items = WishlistItem.objects.filter(user=request.user).select_related('gunung')
    
    wishlist_data = []
    for item in items:
        wishlist_data.append({
            'id': item.id,
            'gunung_id': str(item.gunung.id),  # Convert UUID to string
            'gunung_nama': item.gunung.nama,
            'added_at': item.added_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return JsonResponse(wishlist_data, safe=False)

# Fungsi ini untuk dipanggil oleh AJAX (saat user klik "Add" di hal. Explore)
@login_required(login_url=reverse_lazy('userprofile:login'))
def add_to_wishlist_ajax(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        gunung_id = data.get('gunung_id')
        
        try:
            gunung = get_object_or_404(Gunung, pk=gunung_id)
            
            # Cek apakah sudah ada di wishlist
            if not WishlistItem.objects.filter(user=request.user, gunung=gunung).exists():
                WishlistItem.objects.create(user=request.user, gunung=gunung)
                return JsonResponse({
                    'status': 'success', 
                    'message': f'✓ {gunung.nama} berhasil ditambahkan ke wishlist!'
                })
            else:
                return JsonResponse({
                    'status': 'exists', 
                    'message': f'{gunung.nama} sudah ada di wishlist kamu.'
                })
        except Exception as e:
            return JsonResponse({
                'status': 'error', 
                'message': f'Gagal menambahkan ke wishlist: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'status': 'failed', 
        'message': 'Request tidak valid.'
    }, status=400)

# Fungsi untuk menghapus dari wishlist (via AJAX dari halaman wishlist)
@login_required(login_url=reverse_lazy('userprofile:login'))
def remove_from_wishlist_ajax(request, item_id):
    if request.method == 'POST':
        try:
            item = get_object_or_404(WishlistItem, pk=item_id, user=request.user)
            gunung_nama = item.gunung.nama
            item.delete()
            return JsonResponse({
                'status': 'success', 
                'message': f'✓ {gunung_nama} berhasil dihapus dari wishlist.'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error', 
                'message': f'Gagal menghapus dari wishlist: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'status': 'failed', 
        'message': 'Request tidak valid.'
    }, status=400)