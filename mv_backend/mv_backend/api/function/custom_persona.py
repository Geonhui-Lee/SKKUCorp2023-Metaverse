import json
from django.http import JsonResponse
import wikipedia

persona = """
"""

def get_persona():
    global persona
    return persona

def call(request):
    global persona
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    
    prompt = body['npcname'] + ', ' + body['npcjob']
    persona = wikipedia.summary(prompt, sentences = 4)
    persona += f"\n User's Need: {body['npcgoal']}"
    
    return JsonResponse({
        "persona": persona
    })