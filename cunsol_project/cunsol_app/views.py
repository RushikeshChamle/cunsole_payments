import requests
from django.http import JsonResponse , HttpResponse
import typing
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import users
from .serializers import UserdataSerializer
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.views import View
from .utils.dubbing_utils import download_dubbed_file, wait_for_dubbing_completion
from elevenlabs.client import ElevenLabs
import os
import logging
import jwt
import datetime

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import users
from .serializers import UserdataSerializer


import urllib.parse
from json.decoder import JSONDecodeError


SECRET_KEY = 'Ris#77336#yog!S'  # Replace with your actual secret key

def call_elevenlabs_api(request):
    url = "https://api.elevenlabs.io/v1/dubbing"

    payload = "-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"source_url\"\r\n\r\nhttps://www.youtube.com/watch?v=vZbM80Sj6qY\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"mode\"\r\n\r\nautomatic\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"target_lang\"\r\n\r\nen\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"watermark\"\r\n\r\ntrue\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"dubbing_studio\"\r\n\r\ntrue\r\n-----011000010111000001101001--\r\n\r\n"
    
    headers = {
    "xi-api-key": "474a2f49c67bf56b61f115ce15b41a8e",
    "Content-Type": "multipart/form-data",
    # content_type='multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW'
    
}

    response = requests.request("POST", url, data=payload, headers=headers)


    return JsonResponse(response.json())



def create_dub(request):
    if request.method == 'GET':
        source_url = request.GET.get('source_url')
        source_language = request.GET.get('source_language', 'en')
        target_language = request.GET.get('target_language', 'hi')
        
        ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
        if not ELEVENLABS_API_KEY:
            return JsonResponse({"error": "ELEVENLABS_API_KEY environment variable not found."}, status=500)
        
        client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        
        response = client.dubbing.dub_a_video_or_an_audio_file(
            source_url=source_url,
            target_lang=target_language,
            mode="automatic",
            source_lang=source_language,
            num_speakers=1,
            watermark=True,
        )

        dubbing_id = response.dubbing_id
        if wait_for_dubbing_completion(dubbing_id):
            output_file_path = download_dubbed_file(dubbing_id, target_language)
            return JsonResponse({"success": True, "file_path": output_file_path})
        else:
            return JsonResponse({"success": False, "message": "Dubbing failed or timed out."})
    else:
        return JsonResponse({"error": "Method not allowed."}, status=405)
    


# dubbed file fetching api

logger = logging.getLogger(__name__)
def fetch_file(request, dubbing_id, language_code):
    if request.method == 'GET':
        ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
        if not ELEVENLABS_API_KEY:
            return JsonResponse({"error": "ELEVENLABS_API_KEY environment variable not found."}, status=500)

        logger.info(f"Using ELEVENLABS_API_KEY: {ELEVENLABS_API_KEY}")  # Log the API key to confirm it's being loaded

        url = f"https://api.elevenlabs.io/v1/dubbing/{dubbing_id}/audio/{language_code}"
        headers = {"xi-api-key": ELEVENLABS_API_KEY}

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes

            # Return the file content as a file response
            return HttpResponse(response.content, content_type='audio/mp4')

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch dubbed file: {e}")
            return JsonResponse({"success": False, "message": f"Failed to fetch dubbed file: {str(e)}"}, status=500)
    else:
        return JsonResponse({"error": "Method not allowed."}, status=405)
    



@csrf_exempt
@api_view(['POST'])  # Decorate the view to specify allowed methods
def signup(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Hash the password before saving it to the database
            hashed_password = make_password(data.get('password'))
            data['password'] = hashed_password
            serializer = UserdataSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "User successfully created"}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except JSONDecodeError as e:
            return Response({'error': 'Invalid JSON data'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)



# old sign in API

# @csrf_exempt
# @api_view(['POST'])  # Decorate the view to specify allowed methods  
# def signin(request):
#     if request.method == 'POST':
#         email = request.data.get('email')
#         password = request.data.get('password')
#         user = users.objects.filter(email=email, password=password).first()
#         if user:
#             return Response({"message": "User login successful"})
#         return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    



@csrf_exempt
@api_view(['POST'])
def signin(request):
    if request.method == 'POST':
        email = request.data.get('email')
        password = request.data.get('password')
        user = users.objects.filter(email=email, password=password).first()

        if user:
            payload = {
                'user_id': user.id,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24),
                'iat': datetime.datetime.utcnow()
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
            return Response({"message": "User login successful", "token": token})
        return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    return Response({'message': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@csrf_exempt
def session_data(request, user_id):
    try:
        user = users.objects.get(id=user_id)
    except users.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)

    # Prepare the session data as a dictionary
    session_data = {
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'contact': user.contact,
        # Add any other session data fields you need
    }

    return JsonResponse(session_data)