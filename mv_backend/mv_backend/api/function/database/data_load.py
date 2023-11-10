from django.http import HttpResponse, JsonResponse

from pymongo.mongo_client import MongoClient

from mv_backend.lib.database import Database

import json

def gh_call(request):
    #body_unicode = request.body.decode('utf-8')
    #body = json.loads(body_unicode)

    database = Database()
    client = database.get_client()

    # get all the documents in the collection
    documents = database.get_all_documents('data', 'io')

    # convert to json
    json_documents = []
    for document in documents:
        json_documents.append(document)

    return JsonResponse({
        documents: json_documents
    })