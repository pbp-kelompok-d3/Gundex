from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.db import IntegrityError, transaction 
from .forms import LogPendakianForm
from .models import LogPendakian

def _current_profile(request):
    return request.user

@login_required
def log_list(request):
    prof = _current_profile(request)
    logs = (LogPendakian.objects
            .filter(user=prof)
            .select_related()
            .order_by("-start_date", "-created_at"))
    empty = not logs.exists()
    return render(request, "logpendakian/list.html", {"logs": logs, "empty": empty})

@login_required
def log_create(request):
    if request.method == "POST":
        form = LogPendakianForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            try:
                with transaction.atomic():
                    obj.save()
            except IntegrityError:
                form.add_error(None, "Riwayat untuk gunung & tanggal mulai tersebut sudah ada.")
                html = render_to_string(
                    "logpendakian/partials/form.html",
                    {"form": form, "action_url": reverse("logpendakian:create")},
                    request=request,
                )
                return JsonResponse({"ok": False, "html": html}, status=400)

            row = render_to_string("logpendakian/partials/row.html", {"x": obj}, request=request)
            return JsonResponse({"ok": True, "html": row})
        html = render_to_string(
            "logpendakian/partials/form.html",
            {"form": form, "action_url": reverse("logpendakian:create")},
            request=request,
        )
        return JsonResponse({"ok": False, "html": html}, status=400)
    form = LogPendakianForm()
    html = render_to_string(
        "logpendakian/partials/form.html",
        {"form": form, "action_url": reverse("logpendakian:create")},
        request=request,
    )
    return JsonResponse({"html": html})

@login_required
def log_update(request, pk):
    obj = get_object_or_404(LogPendakian, pk=pk, user=request.user)
    if request.method == "POST":
        form = LogPendakianForm(request.POST, instance=obj)
        if form.is_valid():
            try:
                with transaction.atomic():
                    obj = form.save()
            except IntegrityError:
                form.add_error(None, "Kombinasi gunung & tanggal mulai sudah dipakai di log lain Anda.")
                html = render_to_string(
                    "logpendakian/partials/form.html",
                    {"form": form, "action_url": reverse("logpendakian:update", args=[obj.pk])},
                    request=request,
                )
                return JsonResponse({"ok": False, "html": html}, status=400)
            row = render_to_string("logpendakian/partials/row.html", {"x": obj}, request=request)
            return JsonResponse({"ok": True, "html": row, "id": str(obj.pk)}) 
        html = render_to_string(
            "logpendakian/partials/form.html",
            {"form": form, "action_url": reverse("logpendakian:update", args=[obj.pk])},
            request=request,
        )
        return JsonResponse({"ok": False, "html": html}, status=400)
    form = LogPendakianForm(instance=obj)
    html = render_to_string(
        "logpendakian/partials/form.html",
        {"form": form, "action_url": reverse("logpendakian:update", args=[obj.pk])},
        request=request,
    )
    return JsonResponse({"html": html})


@login_required
def log_delete(request, pk):
    if request.method == "GET":
        obj = get_object_or_404(LogPendakian, pk=pk, user=request.user)
        html = render_to_string(
            "logpendakian/partials/confirm_delete.html",
            {"obj": obj, "request": request},
        )
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"html": html})
        return HttpResponse(html)
    deleted_count, _ = LogPendakian.objects.filter(pk=pk, user=request.user).delete()
    return JsonResponse({
        "ok": bool(deleted_count),
        "id": str(pk)
    })