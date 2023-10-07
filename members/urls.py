from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.main, name='main'),
    path('translate/', views.translate_text, name='translate_text'),
    path('ner_highlight/', views.ner_highlight, name='ner_highlight'),
    path('transcribe_audio/', views.transcribe_audio, name='transcribe_audio'),
]