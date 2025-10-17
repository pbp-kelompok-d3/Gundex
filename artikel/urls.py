from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from artikel.views import index, article_detail, full_article

app_name = 'artikel'

urlpatterns = [
    path('', index, name=''),
    path('article/<uuid:id>/', article_detail, name='article_detail'),
    path('', full_article, name='full_article'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
