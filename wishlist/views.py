from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from .models import WishlistItem
from explore_gunung.models import Gunung
import json

@login_required(login_url=reverse_lazy('userprofile:login'))
def show_wishlist(request):
    items = WishlistItem.objects.filter(user=request.user).select_related('gunung')
    context = {
        'items': items,
        'nama_user': request.user.username,
    }
    return render(request, 'wishlist.html', context)

@login_required(login_url=reverse_lazy('userprofile:login'))
def get_wishlist_json(request):
    items = WishlistItem.objects.filter(user=request.user).select_related('gunung')
    
    wishlist_data = []
    for item in items:
        wishlist_data.append({
            'id': item.id,
            'gunung_id': str(item.gunung.id),
            'gunung_nama': item.gunung.nama,
            'added_at': item.added_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return JsonResponse(wishlist_data, safe=False)

@login_required(login_url=reverse_lazy('userprofile:login'))
def add_to_wishlist_ajax(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        gunung_id = data.get('gunung_id')
        
        try:
            gunung = get_object_or_404(Gunung, pk=gunung_id)
            
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

@csrf_exempt
def flutter_get_wishlist(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            'status': False,
            'message': 'Not authenticated'
        }, status=401)
    
    try:
        items = WishlistItem.objects.filter(user=request.user).select_related('gunung')
        
        wishlist_data = []
        for item in items:
            wishlist_data.append({
                'id': item.id,
                'added_at': item.added_at.strftime('%Y-%m-%d %H:%M:%S'),
                'gunung': {
                    'id': str(item.gunung.id),
                    'nama': item.gunung.nama,
                    'ketinggian': item.gunung.ketinggian,
                    'provinsi': item.gunung.provinsi,
                    'foto': item.gunung.foto,
                    'deskripsi': item.gunung.deksripsi, 
                }
            })
        
        return JsonResponse({
            'status': True,
            'data': wishlist_data
        }, status=200)
        
    except Exception as e:
        return JsonResponse({
            'status': False,
            'message': f'Error: {str(e)}'
        }, status=500)


@csrf_exempt
def flutter_add_to_wishlist(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            'status': False,
            'message': 'Not authenticated'
        }, status=401)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            gunung_id = data.get('gunung_id')
            
            if not gunung_id:
                return JsonResponse({
                    'status': False,
                    'message': 'gunung_id is required'
                }, status=400)
            
            # Get gunung
            try:
                gunung = Gunung.objects.get(pk=gunung_id)
            except Gunung.DoesNotExist:
                return JsonResponse({
                    'status': False,
                    'message': 'Gunung not found'
                }, status=404)
            
            # Check if already exists
            if WishlistItem.objects.filter(user=request.user, gunung=gunung).exists():
                return JsonResponse({
                    'status': False,
                    'message': f'{gunung.nama} sudah ada di wishlist Anda',
                    'already_exists': True
                }, status=200)
            
            # Create wishlist item
            item = WishlistItem.objects.create(user=request.user, gunung=gunung)
            
            return JsonResponse({
                'status': True,
                'message': f'✓ {gunung.nama} berhasil ditambahkan ke wishlist!',
                'data': {
                    'id': item.id,
                    'gunung_id': str(item.gunung.id),
                    'gunung_nama': item.gunung.nama,
                    'added_at': item.added_at.strftime('%Y-%m-%d %H:%M:%S')
                }
            }, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': False,
                'message': 'Invalid JSON'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': False,
                'message': f'Error: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'status': False,
        'message': 'Method not allowed'
    }, status=405)


@csrf_exempt
def flutter_remove_from_wishlist(request, item_id):
    if not request.user.is_authenticated:
        return JsonResponse({
            'status': False,
            'message': 'Not authenticated'
        }, status=401)
    
    if request.method == 'POST':
        try:
            item = get_object_or_404(WishlistItem, pk=item_id, user=request.user)
            gunung_nama = item.gunung.nama
            
            item.delete()
            
            return JsonResponse({
                'status': True,
                'message': f'✓ {gunung_nama} berhasil dihapus dari wishlist'
            }, status=200)
            
        except Exception as e:
            return JsonResponse({
                'status': False,
                'message': f'Error: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'status': False,
        'message': 'Method not allowed'
    }, status=405)


@csrf_exempt
def flutter_check_wishlist_status(request, gunung_id):
    if not request.user.is_authenticated:
        return JsonResponse({
            'status': False,
            'in_wishlist': False,
            'message': 'Not authenticated'
        }, status=200)  
    
    try:
        exists = WishlistItem.objects.filter(
            user=request.user, 
            gunung_id=gunung_id
        ).exists()
        
        return JsonResponse({
            'status': True,
            'in_wishlist': exists
        }, status=200)
        
    except Exception as e:
        return JsonResponse({
            'status': False,
            'in_wishlist': False,
            'message': f'Error: {str(e)}'
        }, status=500)