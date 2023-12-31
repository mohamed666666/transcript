from django.urls import path, include
from . import views
from django.conf.urls.static import static
from django.conf import settings
 
urlpatterns = [
    path('', views.main, name='main'),
    path('translate/', views.translate_text, name='translate_text'),
    path('ner_highlight/', views.ner_highlight, name='ner_highlight'),
    path('transcribe_audio/', views.transcribe_audio, name='transcribe_audio'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)