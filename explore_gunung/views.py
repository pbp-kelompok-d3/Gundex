from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from explore_gunung.models import Gunung
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from explore_gunung.forms import GunungForm
import json

def show_json(request):
    query = request.GET.get('q', '')
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 6))  # default 6 item per page

    gunung_list = Gunung.objects.all()

    if query:
        gunung_list = gunung_list.filter(
            Q(nama__icontains=query) |
            Q(provinsi__icontains=query)
        )

    # Pagination: ambil data sesuai halaman
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

    # Kirim juga apakah masih ada halaman berikutnya
    has_more = end < gunung_list.count()

    return JsonResponse({'results': data, 'has_more': has_more, 'is_admin': request.user.is_admin,})

@login_required(login_url='/userprofile/login/')
def show_gunung(request, id):
    gunung = get_object_or_404(Gunung, pk=id)

    context = {
        'gunung': gunung
    }

    return render(request, "gunung_details.html", context)

def edit_gunung(request, id):
    gunung = get_object_or_404(Gunung, pk=id)
    
    if request.method == 'POST':
        try:
            # 1. BACA DATA DARI BODY JSON
            data = json.loads(request.body)
        except json.JSONDecodeError:
            # Handle jika data bukan JSON yang valid
            return JsonResponse({'success': False, 'message': 'Invalid JSON format'}, status=400)
            
        
        # 2. UPDATE INSTANCE TANPA MENGGUNAKAN FORM
        # Karena kita menerima JSON, lebih mudah update manual
        gunung.nama = data.get('nama', gunung.nama)
        gunung.provinsi = data.get('provinsi', gunung.provinsi)
        gunung.ketinggian = data.get('ketinggian', gunung.ketinggian)
        gunung.deksripsi = data.get('deskripsi', gunung.deksripsi)
        gunung.foto = data.get('foto', gunung.foto)
        
        if not gunung.nama or not gunung.provinsi:
             return JsonResponse({'success': False, 'message': 'Nama dan Provinsi tidak boleh kosong'}, status=400)

        try:
            gunung.save()
            # 3. KEMBALIKAN RESPON JSON SUKSES
            return JsonResponse({'success': True, 'message': 'Data berhasil disimpan'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Gagal menyimpan data: {str(e)}'}, status=500)


    # Jika request bukan POST atau ingin melihat form edit
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
