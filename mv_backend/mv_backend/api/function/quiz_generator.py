import json
from django.http import JsonResponse
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from datetime import datetime
from bson.objectid import ObjectId
import openai

from pymongo.mongo_client import MongoClient

MONGODB_CONNECTION_STRING = "mongodb+srv://geonhui:dotgeon@metaverse.px60xor.mongodb.net/?"
class Database:
    def __init__(self):
        self.client = MongoClient(MONGODB_CONNECTION_STRING)
    
    def get_client(self):
        return self.client

    def get_database(self, database_name):
        return self.client[database_name]

    def get_collection(self, database_name, collection_name):
        return self.get_database(database_name)[collection_name]
    
    def get_all_collections(self, database_name):
        return self.get_database(database_name).list_collection_names()
    
    def get_all_documents(self, database_name, collection_name):
        return self.get_collection(database_name, collection_name).find()
    
    def set_document(self, database_name, collection_name, document):
        return self.get_collection(database_name, collection_name).insert_one(document)
    
    def set_documents(self, database_name, collection_name, documents):
        return self.get_collection(database_name, collection_name).insert_many(documents)

db = Database()
OPENAI_API_KEY = "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"
import os
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
chat = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=1)



npc_template = """
You are a quiz maker. You have to make 5 quizzes(only make 5 quiz) based on what the user is bad at. Make a quiz so that the user can improve its English skills and English communitcation.
The quiz should have a question, 4 choices, a answer, and a explanation. Question, and the explenation must be written in *Korean*, And the choices and the answer must be written in *English*.

user is bad at:
{retrieve}

Make 5 quiz and write it down in a json format.

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
    "quiz3": {...},
    "quiz4": {...},
    "quiz5": {...}
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

  
  
  

  