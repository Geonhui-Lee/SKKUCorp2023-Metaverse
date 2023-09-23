from django.http import HttpResponse, JsonResponse
from mv_backend.mv_backend.api.load import get_body_from_request
from mv_backend.settings import OPENAI_API_KEY
import json, openai

def call(request):
    body = get_body_from_request(request)

    openai.api_key = OPENAI_API_KEY
    openai_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=body["messages"]
    )
    openai_response_message = openai_response["choices"][0]["message"]

    messages_response = body["messages"] + [
        {
            "role": "assistant",
            "content": openai_response_message["content"]
        }
    ]
    
    return JsonResponse({
        "messages": messages_response
    })