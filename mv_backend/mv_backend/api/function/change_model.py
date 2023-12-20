import json
from django.http import JsonResponse
from mv_backend.lib.common import SetModel, CommonChatOpenAI

def call(request):
    global persona
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    SetModel(body['name'])
    print(CommonChatOpenAI().model_name)
    
    return JsonResponse({
       "name": CommonChatOpenAI().model_name
    })