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

CEFR is the English's level criteria established by the Common European Framework of Reference for Languages, which ranges from A1 to C2 (pre-A1,A1,A2,B1,B2,C1,C2).
user's CEFR: {user_cefr}

You are a quiz maker for the User. You have to make 3 quizzes(only make 3 quiz) based on the users CEFR level that helps solve the bad parts user has.
*If* the user is bad at grammer, make a quiz that helps user to learn grammer by referring "user is bad at" and "reason: "(*Never* make a duplicate answer).
*If* the user has a problem with his/hers attitude, make a quiz that helps user to learn how to behave by referring "user is bad at" and "reason: ".
The quiz should have a question, 4 choices, a answer, and a explanation. Question, and the explenation must be written in **KOREAN(한국어로)**(always Korean), And the choices and the answer must be written in *English*.
(The Explenation must inlcude a *specific reason* why the other choices are wrong, and why the answer is correct)
(The choices must have 1 correct answer, and 3 wrong answers)

Make 3 quiz and write it down in a json format. (You can use the example below as a reference)
ex) {example}
"""

example = """{
    "quiz1": {
        "question": "대한민국의 수도는?",
        "choices": ["Seoul", "Busan", "Incheon", "Daegu"],
        "answer": "Seoul",
        "explanation": "서울 (Seoul): 이것이 정답입니다. 서울은 대한민국의 수도로, 국내에서 가장 큰 도시이자 정치, 경제, 문화의 중심지입니다.

부산 (Busan): 부산은 대한민국의 주요 도시 중 하나이지만, 수도가 아닙니다. 부산은 대표적인 항구 도시로서 국제무역과 어업이 발전한 도시입니다.

인천 (Incheon): 인천은 대한민국에서 중요한 도시 중 하나로 국제 공항이 위치해 있습니다. 그러나 수도가 아닌 지방 특별시입니다.

대구 (Daegu): 대구는 대한민국의 도시 중 하나이지만 수도가 아닙니다. 대구는 경제적으로 중요한 역할을 하는 도시 중 하나로 알려져 있습니다.

따라서, "서울"이 대한민국의 수도이며, 다른 선택지는 수도가 아니라는 이유로 틀린 것입니다."
    },
    "quiz2": {...},
    "quiz3": {...}
}"""

npc_prompt = PromptTemplate(
    input_variables= ["retrieve","user_cefr","example"],
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
    user_cefr = db.get_collection(user_name, 'CEFR')
    user_cefr = user_cefr.find_one(sort=[('node', -1)])['cefr']
    print(user_cefr)
    print()

    npc_llm = LLMChain(
    llm=chat,
    prompt=npc_prompt
    )

    npc_response = npc_llm.run(retrieve = retrieve_str,user_cefr = user_cefr,example = example)

    print(npc_response)

    return JsonResponse({
        "npc_response": npc_response
    })