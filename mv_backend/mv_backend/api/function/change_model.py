import json
from django.http import JsonResponse
from mv_backend.lib.common import SetModel, CommonChatOpenAI

#백엔드 상, 전체 모델을 바꾸는 파일
#common.py 내부에 CommonChatOpenAI의 모델을 바꾼다.
#프론트와 통신하는 call 함수
def call(request):
    global persona
    #프론트에서 보내준 값 디코딩
    body_unicode = request.body.decode('utf-8')
    
    #json값 dict로 변환
    body = json.loads(body_unicode)
    
    #프론트에서 보내준 모델 이름으로 백엔드 모델 변경
    SetModel(body['name'])
    
    #프론트에게 디버깅 보내주기
    return JsonResponse({
       "name": CommonChatOpenAI().model_name
    })