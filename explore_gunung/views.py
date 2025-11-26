from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.urls import reverse
from explore_gunung.models import Gunung
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from explore_gunung.forms import GunungForm
from django.views.decorators.csrf import csrf_exempt
import json
import requests

def show_json(request):
    query = request.GET.get('q', '')
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 6))  

    gunung_list = Gunung.objects.all()

    if query:
        gunung_list = gunung_list.filter(
            Q(nama__icontains=query) |
            Q(provinsi__icontains=query)
        )

    start = (page - 1) * limit
    end = start + limit
    paginated_gunung = gunung_list[start:end]

    data = [
        {
            'id': str(g.id),
            'nama': g.nama,
            'ketinggian': g.ketinggian,
            'foto': g.foto,
            'provinsi': g.provinsi,
            'deskripsi': g.deksripsi,
        }
        for g in paginated_gunung
    ]

    has_more = end < gunung_list.count()

    return JsonResponse({'results': data, 'has_more': has_more, 'is_admin': getattr(request.user, 'is_admin', False), 'is_authenticated': request.user.is_authenticated, })

@login_required(login_url='/userprofile/login/')
def show_gunung(request, id):
    gunung = get_object_or_404(Gunung, pk=id)

    context = {
        'gunung': gunung
    }

    return render(request, "gunung_details.html", context)

@csrf_exempt
def edit_gunung(request, id):
    gunung = get_object_or_404(Gunung, pk=id)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON format'}, status=400)
            
        
        gunung.nama = data.get('nama', gunung.nama)
        gunung.provinsi = data.get('provinsi', gunung.provinsi)
        gunung.ketinggian = data.get('ketinggian', gunung.ketinggian)
        gunung.deksripsi = data.get('deskripsi', gunung.deksripsi)
        gunung.foto = data.get('foto', gunung.foto)
        
        if not gunung.nama or not gunung.provinsi:
             return JsonResponse({'success': False, 'message': 'Nama dan Provinsi tidak boleh kosong'}, status=400)

        try:
            gunung.save()
            return JsonResponse({'success': True, 'message': 'Data berhasil disimpan'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Gagal menyimpan data: {str(e)}'}, status=500)


    form = GunungForm(instance=gunung)
    context = {
        'form': form
    }
    return render(request, "edit_gunung.html", context)
    
def get_gunung_json(request, id):
    gunung = get_object_or_404(Gunung, pk=id)
    data = {
        'id': str(gunung.id),
        'nama': gunung.nama,
        'provinsi': gunung.provinsi,
        'ketinggian': gunung.ketinggian,
        'deskripsi': gunung.deksripsi,
        'foto': gunung.foto,
    }
    return JsonResponse(data)

def delete_gunung(request, id):
    gunung = get_object_or_404(Gunung, pk=id)
    gunung.delete()
    return HttpResponseRedirect(reverse('main:show_main'))

def delete_gunung_flutter(request, id):
    if request.method == 'POST':
        gunung = get_object_or_404(Gunung, pk=id)
        
        gunung.delete()
        
        return JsonResponse({
            "status": "success",
            "message": "Data gunung berhasil dihapus."
        }, status=200)
    
    return JsonResponse({
        "status": "error",
        "message": "Invalid request method."
    }, status=401)

def json_all(request):
    query = request.GET.get('q', '')
    gunung_list = Gunung.objects.all()

    if query:
        gunung_list = gunung_list.filter(
            Q(nama__icontains=query) |
            Q(provinsi__icontains=query)
        )
    
    data = [
        {
            'id': str(g.id),
            'nama': g.nama,
            'ketinggian': g.ketinggian,
            'foto': g.foto,
            'provinsi': g.provinsi,
            'deskripsi': g.deksripsi,
        }
        for g in gunung_list
    ]

    return JsonResponse({'results': data})

import requests
from django.http import HttpResponse

def proxy_image(request):
    image_url = request.GET.get('url')
    if not image_url:
        return HttpResponse('No URL provided', status=400)
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }

        response = requests.get(image_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        django_response = HttpResponse(
            response.content,
            content_type=response.headers.get('Content-Type', 'image/jpeg')
        )
        
        django_response["Access-Control-Allow-Origin"] = "*" 
        
        return django_response

    except requests.RequestException as e:
        err_response = HttpResponse(f'Error fetching image: {str(e)}', status=500)
        err_response["Access-Control-Allow-Origin"] = "*"
        return err_response
