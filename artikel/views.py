from django.shortcuts import render, redirect, reverse , get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from artikel.models import Artikel
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.core import serializers
from django.contrib import messages
from django.core.paginator import Paginator
import uuid
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import JsonResponse
import json
import os
from django.contrib.auth.decorators import login_required
# Create your views here.

def full_article(request):
    article_list = Artikel.objects.all().order_by('-id')
    return render(request, 'full_article.html', {'article_list': article_list})

def index(request):
    return render(request, 'full_article.html')

def article_detail(request, id):
    article = get_object_or_404(Artikel, id=id)
    return render(request, 'article_detail.html', {'article': article}) 