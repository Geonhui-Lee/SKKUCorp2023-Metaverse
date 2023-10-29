import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import path

from mv_backend.api.function.hello_world import call as hello_world

from mv_backend.api.function.gpt import call as gpt

from mv_backend.api.function.reflect import call as reflect

from mv_backend.api.function.menu import call as menu

from mv_backend.api.function.database.data_load import gh_call as data_load

from mv_backend.api.function.database.job_prompt import gh_call as job_prompt

def api_render(name, output):
    return path(
        'api/' + name + '/',
        output,
        name=name
    )

def api_path():
    return [
        api_render('test', hello_world),
        api_render('gpt', gpt),
        api_render('reflect', reflect),
        api_render('menu', menu),

        api_render('data/load', data_load),
        api_render('data/job_prompt', job_prompt),
    ]