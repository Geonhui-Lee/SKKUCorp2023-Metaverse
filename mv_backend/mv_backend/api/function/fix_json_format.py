import json
from django.http import JsonResponse
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from datetime import datetime
from bson.objectid import ObjectId
from mv_backend.lib.database import Database
import openai
from pymongo.mongo_client import MongoClient

OPENAI_API_KEY = "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"
import os
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
chat = ChatOpenAI(model_name='gpt-3.5-turbo-1106', temperature=1)



npc_template = """
{input}

this json input has a wrong json format. fix the json format and make it a correct json format.
"""

npc_prompt = PromptTemplate(
    input_variables= ["input"],
    template=npc_template
)

def call(request):

    npc_llm = LLMChain(
    llm=chat,
    prompt=npc_prompt
    )
    print(request.body.decode('utf-8'))
    npc_response = npc_llm.run(input = request.body.decode('utf-8'))
    print()
    print(npc_response)

    return JsonResponse({
        npc_response
    })