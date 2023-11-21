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

CEFR is the English-level criteria established by the Common European Framework of Reference for Languages, which ranges from A1 to C2 (pre-A1, A1, A2, B1, B2, C1, C2).
User's CEFR level: "{user_cefr}"

You are a quiz maker for the User. You have to make 3 quizzes(only make 3 quiz) that matches the CEFR level of the user that helps solve the bad parts user has.
*If* the user is bad at grammer, make a quiz that helps user to learn grammer by referring "user is bad at" and "reason: "
*If* the user has a problem with his/hers attitude, make a quiz that helps user to be polite by referring "user is bad at" and "reason: ".
The quiz should have a question, 4 choices, a answer, and a explanation. Question, and the explenation must be written in **KOREAN(한국어로)**(always Korean), And the choices and the answer must be written in *English*.
(The Explanation must include *specific reason* why the other choices are wrong(*Always* Include *the corrected full sentence* of the incorrect answer.)and why the answer is correct each **KOREAN(한국어로)**(always Korean). )-> the format of the explanation is in the example below.
(The choices must have ***ONLY ONE*** correct answer, and *three* wrong answers).

Make 3 quiz and write it down in a json format.

The order of correct and wrong choices in the example is *not fixed* (*Must* make it in random order). Make quizs that fits "user is bad at" and "reason: ". *Must* include "<color=red>" and "</color>".
ex) {example}

"""

example = """{
    "quiz1": {
        "question": "다음 중 올바른 문장은 무엇인가요?",
        "choices": ["We is playing games.", "They are singing.", "He am reading a book.", "She liking to dance."],
        "answer": "They are singing.",
        "explanation": "1. <color=red>We is playing games.</color> -> <color=green>We are playing games</color>: 주어 'We'에 맞는 동사 'is' 대신 'are'를 사용해야 합니다.2. <color=green>They are singing.</color>: 주어 'They'에 맞는 동사 'are'가 사용되었습니다.3. <color=red>He am reading a book.</color> -> <color=green>He is reading a book.</color>:주어 'He'에 맞는 동사 'am' 대신 'is'를 사용해야 합니다.4. <color=red>She liking to dance.</color> -> <color=green>She likes to dance.</color>:'She'와 'liking'이 함께 사용될 때는 동사의 기본형이 사용되어야 합니다. "
    },
    "quiz2": {...},
    "quiz3": {...}
}"""
example1 = """{
    "quiz1": {
        "question": "question content",
        "choices": ["wrong choice1", "correct choice", "wrong choice2", "wrong choice3"],
        "answer": "answer cotent",
        "explanation": "1. <color=red>wrong sentence</color> -> <color=green>correct sentence</color>: explanation1 content 2. <color=green>They are singing.</color>: explanation2 content 3. <color=red>wrong sentence</color> -> <color=green>correct sentence</color>:explanation3 content   4. <color=red>wrong sentenc</color> -> <color=green>correct sentence</color>:explanation4 content"
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
    cefr_collection = db.get_collection(user_name, 'CEFR')
    #가장 최근의 cefr 가져오기
    cefr = cefr_collection.find_one(sort=[('node', -1)])['cefr']
    print(cefr)
    print()

    npc_llm = LLMChain(
    llm=chat,
    prompt=npc_prompt
    )

    npc_response = npc_llm.run(retrieve = retrieve_str,user_cefr = cefr ,example = example)

    print(npc_response)

    return JsonResponse({
        "npc_response": npc_response
    })