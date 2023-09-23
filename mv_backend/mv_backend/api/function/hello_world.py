from django.http import HttpResponse, JsonResponse

def call(request):
    return JsonResponse({
        "messages": [
            {
                "role": "assistant",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": "Hello!"
            }
        ]
    })