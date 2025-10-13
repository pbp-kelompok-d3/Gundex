from django.http import JsonResponse
from explore_gunung.models import Gunung
from django.shortcuts import render

def show_json(request):
    # Dapatkan parameter 'q' (query/kata kunci) dari request AJAX
    query = request.GET.get('q', '') 
    
    # Mulai dengan semua objek
    gunung_list = Gunung.objects.all()

    # Jika ada kata kunci (query), filter hasilnya
    if query:
        # Gunakan Q objects (diperlukan import) untuk logika OR (Nama ATAU Provinsi)
        from django.db.models import Q 
        
        gunung_list = gunung_list.filter(
            Q(nama__icontains=query) | # Cari di kolom 'nama' (icontains = case-insensitive contains)
            Q(provinsi__icontains=query) # Cari di kolom 'provinsi'
        )

    # Lanjutkan proses serialisasi data
    data = [
        {
            'id': str(gunung.id),
            'nama': gunung.nama,
            'ketinggian': gunung.ketinggian,
            'foto': gunung.foto,
            'provinsi': gunung.provinsi,
            'deskripsi': gunung.deksripsi,
        }
        for gunung in gunung_list
    ]

    return JsonResponse(data, safe=False)