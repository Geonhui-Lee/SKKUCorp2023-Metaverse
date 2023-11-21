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
# chat = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)
chat = CommonChatOpenAI()
###prompt
translate_template = """
content:
{content}

Translate the content into *Korean*. Do not translate (reason: ,  -> ).
Do not show "None" content. Do not show bracket content.
example:
문법 실수:
1. 주어-동사 일치 | 이유: "No I didn't likes them" -> "No, I didn't like them."
2. ...
format:
문법 실수:
1. (korean) | 이유: (english)
2. ...
"""
translate_prompt = PromptTemplate(
    input_variables=["content"], template=translate_template
)

translate = LLMChain(
    llm=chat,
    prompt=translate_prompt
)
###
reflect_translate_template = """
content:
{content}

Translate the content into *Korean*. Do not translate (reason: ,  -> ).
Do not show "None" content. Do not show bracket content.
example:
관심사: (korean)
대화 성향: (korean)
대화 주제: (korean)
"""
reflect_translate_prompt = PromptTemplate(
    input_variables=["content"], template=reflect_translate_template
)

reflect_translate = LLMChain(
    llm=chat,
    prompt=reflect_translate_prompt
)
# important_template = """
# Find {num} important dialogues in the following conversation of {name}.

# Conversation: 
# {event}

# Ranking:
# [1]"""

# important_prompt = PromptTemplate(
#     input_variables=["event", "name", "num"], template=important_template
# )

# important_query = LLMChain(
#     llm=chat,
#     prompt=important_prompt
# )

def call(request):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    opponent = ""
    for chat_data in body["messages"]:
        if chat_data["role"] == "npc_name":
            opponent = chat_data["content"]
            break
        
    user_name = ""
    for chat_data in body["messages"]:
        if chat_data["role"] == "user_name":
            user_name = chat_data["content"]
            break
    
    memory = memory_dict.get(user_name)

    conversation = Database.get_all_documents(db, user_name, "Conversations")
    print(conversation)
    node = 0
    data_num = 0

    for i in conversation:
        data_num += 1
    
    if data_num != 0:
        node = i["node"] + 1
    
    datetimeStr = datetime.now().strftime("%Y-%m-%d")

    history = memory.load_memory_variables({})['chat_history']
    chat_data_list = list()
    user_chat_data_list = list()
    for message in history:
        if type(message) == HumanMessage:
            chat_data_list.append(user_name + ": " + message.content)
            user_chat_data_list.append(user_name + ": " + message.content)
            document_user = {"_id":ObjectId(),"node":node,"timestamp":datetimeStr,"memory":message.content,"name":user_name,"opponent":opponent}
            print(Database.set_document(db, user_name, "Memory", document_user))
            node += 1
        elif type(message) == AIMessage:
            chat_data_list.append(opponent + ": " + message.content)
            document_user = {"_id":ObjectId(),"node":node,"timestamp":datetimeStr,"memory":message.content,"name":opponent,"opponent":user_name}
            print(Database.set_document(db, user_name, "Memory", document_user))
            node += 1 
        else:
            document_user = {"_id":ObjectId(),"node":node,"timestamp":datetimeStr,"memory":message.content,"name":"summary","opponent":"summary"}
            print(Database.set_document(db, user_name, "Memory", document_user))
            node += 1
            
    
    for chat_data in body["messages"]:
        if chat_data["role"] == user_name:
            chat_data_list.append(chat_data["role"] + ": " + chat_data["content"])
            user_chat_data_list.append(chat_data["role"] + ": " + chat_data["content"])
            document_user = {"_id":ObjectId(),"node":node,"timestamp":datetimeStr,"memory":chat_data["content"],"name":user_name,"opponent":opponent}
            print(Database.set_document(db, user_name, "Conversations", document_user))
            node += 1
        if chat_data["role"] == opponent:
            chat_data_list.append(chat_data["role"] + ": " + chat_data["content"])
            document_user = {"_id":ObjectId(),"node":node,"timestamp":datetimeStr,"memory":chat_data["content"],"name":opponent,"opponent":user_name}
            print(Database.set_document(db, user_name, "Conversations", document_user))
            node += 1
    
    # conversation = Database.get_all_documents(db, user_name, "Conversations")
    # print(conversation)
    # node = 0
    # data_num = 0

    # for i in conversation:
    #     data_num += 1
    
    # if data_num != 0:
    #     node = i["node"] + 1
    
    if(memory):
        memory.clear

    #retrieve_document = retrieve(opponent, user_name, chat_data_list)
    ##reflect_document = reflect(opponent, user_name, chat_data_list)
    retrieve_content = retrieve(opponent, user_name, chat_data_list)
    reflect_content = reflect(opponent, user_name, chat_data_list)
    cefr_content = cefr(user_name, user_chat_data_list)

    retrieve_korean = translate.run(content = retrieve_content)
    reflect_korean = reflect_translate.run(content = reflect_content)

    previous = Database.get_all_documents(db, user_name, "Retrieves_Kor")
    print(previous)
    data_num = 0
    node = 0

    for i in previous:
        data_num += 1
    
    if data_num != 0:
        print(i)
        node = i["node"]
        node += 1
    
    datetimeStr = datetime.now().strftime("%Y-%m-%d")
    document_user = {"_id":ObjectId(),"node":node,"timestamp":datetimeStr,"retrieve":retrieve_korean,"name":opponent}
    print(Database.set_document(db, user_name, "Retrieves_Kor", document_user))

    previous = Database.get_all_documents(db, user_name, "Reflects_Kor")
    print(previous)
    data_num = 0
    node = 0

    for i in previous:
        data_num += 1
    
    if data_num != 0:
        print(i)
        node = i["node"]
        node += 1
    
    document_user = {"_id":ObjectId(),"node":node,"timestamp":datetimeStr,"reflect":reflect_korean,"name":opponent}
    print(Database.set_document(db, user_name, "Reflects_Kor", document_user))
    
    messages_response = [
        {
            "role": "reflect",
            "content": reflect_korean
        }
    ]

    messages_response += [
        {
            "role": "retrieve",
            "content": retrieve_korean
        }
    ]

    messages_response += [
        {
            "role": "cefr",
            "content": cefr_content
        }
    ]

    print(messages_response)
    
    return JsonResponse({
        "messages": messages_response
    })