import json
from django.http import JsonResponse
from langchain.tools import WikipediaQueryRun
from langchain.utilities import WikipediaAPIWrapper

wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())

persona = """
"""

def get_persona():
    global persona
    return persona

def call(request):
    global persona
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    
    prompt = body['npcjob'] + ', ' + body['npcname']
    persona = wikipedia.run(prompt).split('Page:')[1].split('Summary:')[1]
    persona += f"\n Mission: {body['npcgoal']}"
    
    return JsonResponse({
        "persona": persona
    })