import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import path


from mv_backend.api.function.chat import call as gpt
#from mv_backend.api.function.chat_improved import call as gpt
from mv_backend.api.function.custom_persona import call as custom_persona

from mv_backend.api.function.change_model import call as change_model

from mv_backend.api.function.retrieve import retrieve as retrieve

from mv_backend.api.function.reflect import reflect as reflect

from mv_backend.api.function.quiz_generator import call as quiz_generator

from mv_backend.api.function.fix_json_format import call as fix_json_format

from mv_backend.api.function.current import call as current

from mv_backend.api.function.profile import call as profile

from mv_backend.api.function.session_end import call as session_end

from mv_backend.pages.report import gh_render as report_page

def api_render(name, output):
    return path(
        'api/' + name + '/',
        output,
        name=name
    )

def api_path():
    return [
        api_render('gpt', gpt),
        api_render('retrieve', retrieve),
        api_render('reflect', reflect),
        api_render('current', current),
        api_render('profile', profile),
        api_render('session_end', session_end),
        api_render('quiz_generator', quiz_generator),
        api_render('fix_json_format', fix_json_format),
        api_render('custom_persona', custom_persona),
        api_render('change_model', change_model),

        path('report/', report_page, name='report')
    ]