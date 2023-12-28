#Customizing NPC의 persona 생성 파일
import json
from django.http import JsonResponse
import wikipedia

persona = """
"""

#persona값을 다른 파일에서 받아갈 수 있는 함수
def get_persona():
    global persona
    return persona

#프론트와 통신하는 call 함수
def call(request):
    global persona
    #프론트에서 보내준 값 디코딩
    body_unicode = request.body.decode('utf-8')
    
    #json값 dict로 변환
    body = json.loads(body_unicode)
    
    #wikipeida Query 생성("이름, 직업")
    prompt = body['npcname'] + ', ' + body['npcjob']
    
    #wikipeida 요약문 가져오기(query ,sentences는 요약할 문장 길이)
    persona = wikipedia.summary(prompt, sentences = 4)
    
    #User가 알고 싶은 것 persona에 추가
    persona += f"\n User's Need: {body['npcgoal']}"
    
    #프론트에게 디버깅 보내주기
    return JsonResponse({
        "persona": persona
    })