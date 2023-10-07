from django.http import HttpResponse
from django.template import loader
from django.http import JsonResponse
from googletrans import Translator
import spacy
from django.views.decorators.csrf import csrf_exempt
import os
from django.views.decorators.http import require_POST
from whisper import load_model
import tempfile
import whisper
from pathlib import Path
from django.middleware.csrf import get_token
from vosk import Model, KaldiRecognizer
import json
from channels.generic.websocket import AsyncWebsocketConsumer

def main(request, first_name=None, last_name=None, id=None):
    
    context = {
        'first_name': first_name,
        'last_name': last_name,
        'id': id,
    }
    template = loader.get_template('main.html')
    return HttpResponse(template.render(context, request))

def translate_text(request):
    if request.method == 'POST':
        text = request.POST.get('text', '')
        target_language = request.POST.get('target_language', 'en')  # Default to English

        try:
            translator = Translator()
            translated_text = translator.translate(text, dest=target_language)

            return JsonResponse({'translated_text': translated_text.text})
        except Exception as e:
            # Handle the exception and return an error JSON response
            return JsonResponse({'error': f'Translation error: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def ner_highlight(request):
    a = 1
    language_models = {
        'en': 'en_core_web_sm',
        'es': 'es_core_news_sm',
        'it': 'it_core_news_sm',
    }
    language = request.POST.get('language', '')
    if language[:2] == 'ar':
        return
    else:
        if language[:2] in language_models:
                nlp = spacy.load(language_models[language[:2]])
        else:
            nlp = spacy.load('en_core_web_sm')  # Default to English if language is not supported
        if request.method == 'POST':
            text = request.POST.get('text', '')

            # Process the text with spaCy NER
            doc = nlp(text)

            # Extract named entities and apply highlighting
            highlighted_text = ""
            c = 0

            for token in doc:
                if token.ent_type_:
                    highlighted_text += f'<mark>{token.text}</mark> '
                    c += 1
                else:
                    highlighted_text += f'{token.text} '
                    c += 1
                if c%6 == 0:
                    highlighted_text += "<br>"
                    highlighted_text += a * '&nbsp;'
                    a += 1
                    c = 0

            # Return the highlighted text in the response
            return JsonResponse({'highlighted_text': highlighted_text.rstrip()})

    return JsonResponse({'error': 'Invalid request method'})

@csrf_exempt
@require_POST
def transcribe_audio(request):
    a = 1
    if 'audio' in request.FILES:
        audio_file = request.FILES['audio']

        # Create a temporary file to store the uploaded audio
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio:
            for chunk in audio_file.chunks():
                temp_audio.write(chunk)

        try:
            # Load the Whisper model
            BASE_DIR = Path(__file__).resolve().parent.parent
            #model = whisper.load_model(BASE_DIR / 'members' / 'whisper1' / 'small.pt')
            model = whisper.load_model('tiny')

            # Transcribe the audio using the Whisper model
            result = model.transcribe(temp_audio.name)
            transcription_text = result["text"]
            transcription_text = transcription_text.split()
            for i, word in enumerate(transcription_text):
                if word[-1] == '.':
                    transcription_text[i] = word + '<br>'
            transcription = ''
            
            for i in transcription_text:
                if i.strip()[-1] == '.':
                    transcription += i + (a * '&nbsp;')
                    a += 1
                else:
                    transcription += i + ' '

            return JsonResponse({'transcription': transcription})
        except Exception as e:
            os.remove(temp_audio.name)  # Remove the temporary audio file in case of an error

            # Handle the error as needed
            return JsonResponse({'error': 'Transcription failed'}, status=400)

    return JsonResponse({'error': 'No audio file provided'}, status=400)

# Function to get CSRF token
def getCSRFToken(request):
    return get_token(request)