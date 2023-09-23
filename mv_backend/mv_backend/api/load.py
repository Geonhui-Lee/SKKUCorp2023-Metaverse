import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import path

from mv_backend.api.function.hello_world import call as hello_world

from mv_backend.api.function.gpt import call as gpt

def get_body_from_request(request):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    return body

def api_render(name, output):
    return path(
        'api/' + name + '/',
        output,
        name=name
    )

def api_path():
    return [
        api_render('test', hello_world),
        api_render('gpt', gpt)
    ]