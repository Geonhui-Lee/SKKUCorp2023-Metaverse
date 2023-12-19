import json
from django.http import JsonResponse
from langchain.tools import WikipediaQueryRun
from langchain.utilities import WikipediaAPIWrapper

wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())

persona = """
"""

def call(request):
    global persona
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    
    prompt = body['messages'][0]['npcjob'] + ', ' + body['messages'][0]['npcname']
    persona = wikipedia.run(prompt).split('Page:')[1].split('Summary:')[1]
    persona += f"\n Mission: {body['messages'][0]['npcgoal']}"
    persona = list(persona)
    
    return JsonResponse({
        "messages": persona
    })