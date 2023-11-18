import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import path

from mv_backend.api.function.hello_world import call as hello_world

from mv_backend.api.function.chat import call as gpt

from mv_backend.api.function.retrieve import retrieve as retrieve

from mv_backend.api.function.reflect import reflect as reflect

from mv_backend.api.function.plan import call as plan

from mv_backend.api.function.menu import call as menu

from mv_backend.api.function.quiz_generator import call as quiz_generator

from mv_backend.api.function.current import call as current

from mv_backend.api.function.session_end import call as session_end

from mv_backend.api.function.database.data_load import gh_call as data_load

from mv_backend.api.function.database.job_prompt import gh_call as job_prompt

from mv_backend.pages.report import gh_render as report_page

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
        api_render('retrieve', retrieve),
        api_render('reflect', reflect),
        api_render('plan', plan),
        api_render('menu', menu),
        api_render('current', current),
        api_render('session_end', session_end),
        api_render('data/load', data_load),
        api_render('data/job_prompt', job_prompt),
        api_render('quiz_generator', quiz_generator),

        path('report/', report_page, name='report')
    ]