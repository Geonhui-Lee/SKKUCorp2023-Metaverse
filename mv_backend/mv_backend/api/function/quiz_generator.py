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

MONGODB_CONNECTION_STRING = "mongodb+srv://geonhui:dotgeon@metaverse.px60xor.mongodb.net/?"

db = Database()
OPENAI_API_KEY = "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"
import os
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
chat = ChatOpenAI(model_name='gpt-3.5-turbo-1106', temperature=1)



npc_template = """
user is bad at:
{retrieve}

You are a quiz maker for the User. You have to make 3 quizzes(only make 3 quiz) that helps solve the bad parts user has.
*If* the user is bad at grammer, make a quiz that helps user to learn grammer by referring "user is bad at"(*Never* make a duplicate answer).
*If* the user has a problem with his/hers attitude, make a quiz that helps user to learn how to behave by referring "user is bad at".
The quiz should have a question, 4 choices, a answer, and a explanation. Question, and the explenation must be written in **KOREAN(한국어로)**(always Korean), And the choices and the answer must be written in *English*.
(The Explenation must inlcude why the other choices are wrong, and why the answer is correct)
(The choices must have 1 correct answer, and 3 wrong answers)

Make 3 quiz and write it down in a json format.

ex) {example}
"""

example = """{
    "quiz1": {
        "question": "대한민국의 수도는?",
        "choices": ["Seoul", "Busan", "Incheon", "Daegu"],
        "answer": "Seoul",
        "explanation": "서울은 대한민국의 수도이다."
    },
    "quiz2": {...},
    "quiz3": {...}
}"""

npc_prompt = PromptTemplate(
    input_variables= ["retrieve", "example"],
    template=npc_template
)

def call(request):
    body_unicode = request.body.decode('utf-8') 
    body = json.loads(body_unicode)

    user_name = body['username']

    retrieve_collection = db.get_collection(user_name, 'Retrieves')
    last_retrieves = list(retrieve_collection.find(sort=[('node', -1)], limit=3))
    retrieve_str = '\n'.join([r['retrieve'] for r in last_retrieves[::-1]])
    print(retrieve_str)
    print()

    npc_llm = LLMChain(
    llm=chat,
    prompt=npc_prompt
    )

    npc_response = npc_llm.run(retrieve = retrieve_str, example = example)

    print(npc_response)

    return JsonResponse({
        "npc_response": npc_response
    })