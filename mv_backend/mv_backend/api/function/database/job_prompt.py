from django.http import HttpResponse, JsonResponse

from pymongo.mongo_client import MongoClient

from mv_backend.lib.database import Database

import json

def gh_call(request):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    # get the character name from the request body
    character_job = body['job']

    database = Database()
    client = database.get_client()

    # get all the documents in the collection
    documents = database.get_all_documents('npc', 'preset')
    # documents = {
    #     'name': 'Daniel',
    #     'prompt': {
    #         'system': "Daniel has a guy who likes to draw."
    #     },
    #     'characteristics': {
    #         'job': "artist"
    #     }
    # }

    # convert to json
    #json_documents = []
    prompt = {}
    for document in documents:
        if (document['job'] == character_job):
            prompt = document.prompt
            #json_documents.append(document.prompt)

    return JsonResponse({
        'prompt': prompt
    })