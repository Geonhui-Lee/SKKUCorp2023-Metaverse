from django.http import HttpResponse, JsonResponse
from mv_backend.lib.database import Database
from mv_backend.settings import OPENAI_API_KEY
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from mv_backend.api.function.retrieve_auto_test import *
from mv_backend.api.function.reflect_auto_test import *
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
import os
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
memory = ConversationBufferMemory(memory_key="chat_history", input_key= "user_input")
chat = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)

###prompt
important_template = """
Find {num} important dialogues in the following conversation of {name}.

Conversation: 
{event}

Ranking:
[1]"""

important_prompt = PromptTemplate(
    input_variables=["event", "name", "num"], template=important_template
)

important_query = LLMChain(
    llm=chat,
    prompt=important_prompt
)

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

    user_num_data = 0
    opponent_num_data = 0
    user_chat_data_string = ""
    opponent_chat_data_string = ""

    for chat_data in body["messages"]:
        if chat_data["role"] == user_name:
            user_chat_data_string += chat_data["content"] + "\n"
            user_num_data += 1
        if chat_data["role"] == opponent:
            opponent_chat_data_string += chat_data["content"] + "\n"
            opponent_num_data += 1

    if user_num_data > 10:
        user_num_data = 10
    if opponent_num_data > 10:
        opponent_num_data = 10
    
    conversation = Database.get_all_documents(db, user_name, "Conversations")
    print(conversation)
    node = 0
    data_num = 0

    for i in conversation:
        data_num += 1
    
    if data_num != 0:
        node = i["node"] + 1
    
    datetimeStr = datetime.now().strftime("%Y-%m-%d")
    user_result = important_query.run(event = user_chat_data_string, name = user_name, num = user_num_data)
    opponent_result = important_query.run(event = opponent_chat_data_string, name = opponent, num = opponent_num_data)

    user_save_data = user_result.split("\n")
    opponent_save_data = opponent_result.split("\n")

    for i in user_save_data:
        document_user = {"_id":ObjectId(),"node":node,"timestamp":datetimeStr,"memory":i,"name":user_name,"opponent":opponent}
        print(Database.set_document(db, user_name, "Conversations", document_user))
    for i in opponent_save_data:
        document_opponent = {"_id":ObjectId(),"node":node,"timestamp":datetimeStr,"memory":i,"name":opponent,"opponent":user_name}
        print(Database.set_document(db, user_name, "Conversations", document_opponent))
    
    retrieve(opponent, user_name)
    reflect(opponent, user_name)

    messages_response = body["messages"] + [
        {
            "role": opponent,
            "content": "end"
        }
    ]
    
    return JsonResponse({
        "messages": messages_response
    })