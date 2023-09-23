from django.http import HttpResponse, JsonResponse
from mv_backend.settings import OPENAI_API_KEY
import openai

def call(request):
    openai.api_key = OPENAI_API_KEY

    messages_request = request["messages"]

    openai_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages_request
    )

    messages_response = messages_response + [
        {
            "role": "assistant",
            "content": openai_response["choices"][0]["text"]
        }
    ]
    
    return JsonResponse({
        "messages": messages_response
    })