from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import LogPendakian
from .forms import LogPendakianForm

@login_required
def log_list(request):
    logs = LogPendakian.objects.filter(user=request.user).order_by("-start_date", "-created_at")
    return render(request, "LogPendakian/list.html", {"logs": logs})

@login_required
def log_create(request):
    if request.method == "POST":
        form = LogPendakianForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            return redirect(reverse("LogPendakian:list"))
    else:
        form = LogPendakianForm()
    return render(request, "LogPendakian/form.html", {"form": form})

@login_required
def log_update(request, pk):
    obj = get_object_or_404(LogPendakian, pk=pk, user=request.user)
    if request.method == "POST":
        form = LogPendakianForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect(reverse("LogPendakian:list"))
    else:
        form = LogPendakianForm(instance=obj)
    return render(request, "LogPendakian/form.html", {"form": form, "object": obj})

@login_required
def log_delete(request, pk):
    obj = get_object_or_404(LogPendakian, pk=pk, user=request.user)
    if request.method == "POST":
        obj.delete()
        return redirect(reverse("LogPendakian:list"))
    return render(request, "LogPendakian/confirm_delete.html", {"object": obj})
