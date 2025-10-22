from django.http import JsonResponse
from explore_gunung.models import Gunung
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

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

    return JsonResponse({'results': data, 'has_more': has_more})

def show_gunung(request, id):
    gunung = get_object_or_404(Gunung, pk=id)

    context = {
        'gunung': gunung
    }

    return render(request, "gunung_details.html", context)
