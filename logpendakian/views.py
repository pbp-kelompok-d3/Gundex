import json
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from explore_gunung.models import Gunung
from .forms import LogPendakianForm
from .models import LogPendakian

def _current_profile(request):
    return request.user

@login_required(login_url='/userprofile/login/')
def log_list(request):
    prof = _current_profile(request)
    logs = (LogPendakian.objects
            .filter(user=prof)
            .select_related()
            .order_by("-start_date", "-created_at"))
    empty = not logs.exists()
    return render(request, "logpendakian/list.html", {"logs": logs, "empty": empty})

@login_required(login_url='/userprofile/login/')
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

@login_required(login_url='/userprofile/login/')
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


@login_required(login_url='/userprofile/login/')
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

# integrating to the flutter

# @login_required(login_url='/userprofile/login/')
def log_list_json(request):
    if request.user.is_authenticated:
        logs = (
            LogPendakian.objects
            .filter(user=request.user)
            .select_related("gunung")
            .order_by("-start_date", "-created_at")
        )
    else:
        logs = LogPendakian.objects.none()

    results = []
    for log in logs:
        results.append({
            "id": str(log.id),
            "gunung_id": str(log.gunung_id) if log.gunung_id else None,
            "gunung_nama": getattr(log.gunung, "nama", None)
                if getattr(log, "gunung", None) else None,
            "start_date": log.start_date.isoformat()
                if getattr(log, "start_date", None) else None,
            "end_date": log.end_date.isoformat()
                if getattr(log, "end_date", None) else None,
            "notes": log.notes,
            "summit_reached": log.summit_reached,
            "team_size": log.team_size,
            "rating": log.rating,
            "duration_days": log.duration_days,
            "photo_url": getattr(log.gunung, "foto", None),
        })

    return JsonResponse({"results": results})


# @login_required(login_url='/userprofile/login/')
def log_detail_json(request, pk):
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Unauthorized"}, status=401)

    log = get_object_or_404(LogPendakian, pk=pk, user=request.user)
    return JsonResponse(serialize_log(log))


def serialize_log(log: LogPendakian) -> dict:
    return {
        "id": str(log.id),
        "gunung_id": str(log.gunung_id) if log.gunung_id else None,
        "gunung_nama": getattr(log.gunung, "nama", None)
            if getattr(log, "gunung", None) else None,
        "start_date": log.start_date.isoformat()
            if getattr(log, "start_date", None) else None,
        "end_date": log.end_date.isoformat()
            if getattr(log, "end_date", None) else None,
        "notes": log.notes,
        "summit_reached": log.summit_reached,
        "team_size": log.team_size,
        "rating": log.rating,
        "duration_days": log.duration_days,
        "photo_url": getattr(log.gunung, "foto", None),
    }

@csrf_exempt
@require_http_methods(["POST"])
def log_create_api(request):
    if not request.user.is_authenticated:
        return JsonResponse(
            {"success": False, "error": "Unauthorized"},
            status=401,
        )

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "error": "Invalid JSON"},
            status=400,
        )

    gunung_id = payload.get("gunung_id")
    if not gunung_id:
        return JsonResponse(
            {"success": False, "error": "gunung_id is required"},
            status=400,
        )

    try:
        gunung = Gunung.objects.get(pk=gunung_id)
    except Gunung.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Gunung not found"},
            status=404,
        )

    start_date = parse_date(payload.get("start_date") or "")
    end_date = parse_date(payload.get("end_date") or "")
    notes = (payload.get("notes") or "").strip()

    if not start_date:
        return JsonResponse(
            {"success": False, "error": "start_date is required"},
            status=400,
        )

    log = LogPendakian(
        user=request.user,
        gunung=gunung,
        start_date=start_date,
        end_date=end_date,
        summit_reached=bool(payload.get("summit_reached", False)),
        team_size=payload.get("team_size") or 1,
        rating=payload.get("rating"),
        notes=notes,
    )

    try:
        log.full_clean()
        log.save()
    except (ValidationError, IntegrityError) as e:
        return JsonResponse(
            {"success": False, "error": str(e)},
            status=400,
        )

    return JsonResponse(
        {"success": True, "log": serialize_log(log)},
        status=201,
    )


@csrf_exempt
@require_http_methods(["POST"])
def log_update_api(request, pk):
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "Unauthorized"}, status=401)

    log = get_object_or_404(LogPendakian, pk=pk, user=request.user)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

    gunung_id = payload.get("gunung_id")
    if gunung_id:
        try:
            gunung = Gunung.objects.get(pk=gunung_id)
        except Gunung.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "Gunung not found"},
                status=404,
            )
        log.gunung = gunung

    start_date = parse_date(payload.get("start_date") or "")
    end_date = parse_date(payload.get("end_date") or "")

    if start_date:
        log.start_date = start_date
    if end_date:
        log.end_date = end_date

    log.summit_reached = bool(payload.get("summit_reached", log.summit_reached))
    if "team_size" in payload:
        log.team_size = payload.get("team_size") or 1
    if "rating" in payload:
        log.rating = payload.get("rating")
    if "notes" in payload:
        log.notes = (payload.get("notes") or "").strip()
    try:
        log.full_clean()
        log.save()
    except (ValidationError, IntegrityError) as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)

    return JsonResponse({"success": True, "log": serialize_log(log)})


@csrf_exempt
@require_http_methods(["POST"])
def log_delete_api(request, pk):
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "Unauthorized"}, status=401)

    log = get_object_or_404(LogPendakian, pk=pk, user=request.user)
    log.delete()
    return JsonResponse({"success": True})

