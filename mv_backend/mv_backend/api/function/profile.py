from django.http import HttpResponse, JsonResponse
from mv_backend.lib.database import Database
from mv_backend.settings import OPENAI_API_KEY
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from mv_backend.lib.common import CommonChatOpenAI, gpt_model_name
from mv_backend.api.function.retrieve import *
from mv_backend.api.function.reflect import *
from mv_backend.api.function.cefr import *
from mv_backend.api.function.chat import memory_dict
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
import json, openai
from datetime import datetime
from bson.objectid import ObjectId

db = Database()

openai.api_key = OPENAI_API_KEY

chat = CommonChatOpenAI()

def call(request):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    user_name = ""
    for chat_data in body["messages"]:
        if chat_data["role"] == "user_name":
            user_name = chat_data["content"]
            break
    
    reflect = Database.get_recent_documents(db, user_name, "Reflects_Kor", 3)
    retrieve = Database.get_recent_documents(db, user_name, "Retrieves_Kor", 3)
    cefr = Database.get_recent_documents(db, user_name, "CEFR_GPT", 1)
    interest_dict = dict()
    coversationStyle_dict = dict()
    cefr_string = ""
    data_num = 0
    for i in reflect:
        result = i["reflect"].split(":")
        interests = result[1].split('\n')[0].split(",")
        for interest in interests:
            if interest not in interest_dict.keys():
                interest_dict[interest] = 1
            else:
                interest_dict[interest] += 1
        conversationStyles = result[2].split('\n')[0].split(",")
        if (data_num == 0):
            for conversationStyle in conversationStyles:
                if conversationStyle not in coversationStyle_dict.keys():
                    coversationStyle_dict[conversationStyle] = 1
                else:
                    coversationStyle_dict[conversationStyle] += 1
        data_num += 1
    
    data_num = 0
    
    retrieve_dict = dict()
    for i in retrieve:
      result = i["retrieve"].split("이유:")
      print(result)
      length = len(result)
      for j in range(length-1):
        retrieve_result = result[j+1].split('\n')[0]
        if retrieve_result not in retrieve_dict.keys():
            retrieve_dict[retrieve_result] = 1
        else:
            retrieve_dict[retrieve_result] += 1
    for i in cefr:
      cefr_string += i["cefr"]
    
    sorted_interest = list(dict(sorted(interest_dict.items(), key = lambda item: item[1], reverse = True)).keys())
    sorted_conversationStyle = list(dict(sorted(coversationStyle_dict.items(), key = lambda item: item[1], reverse = True)).keys())
    sorted_retrieve = list(dict(sorted(retrieve_dict.items(), key = lambda item: item[1], reverse = True)).keys())
    
    messages_response = [
        {
            "role": "interest",
            "content": str(sorted_interest).removeprefix('[').removesuffix(']').replace("'", "")
        }
    ]
    
    messages_response += [
        {
            "role": "conversationStyle",
            "content": str(sorted_conversationStyle).removeprefix('[').removesuffix(']').replace("'", "")
        }
    ]

    messages_response += [
        {
            "role": "retrieve",
            "content": str(sorted_retrieve).removeprefix('[').removesuffix(']').replace("'", "")
        }
    ]

    messages_response += [
        {
            "role": "cefr",
            "content": cefr_string
        }
    ]

    print(messages_response)
    
    return JsonResponse({
        "messages": messages_response
    })