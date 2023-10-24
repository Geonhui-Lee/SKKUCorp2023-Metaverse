from django.http import HttpResponse, JsonResponse
from mv_backend.mv_backend.lib.database import Database
from mv_backend.settings import OPENAI_API_KEY
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
import json, openai
import uuid
from datetime import datetime
from bson.objectid import ObjectId

db = Database()

openai.api_key = OPENAI_API_KEY
import os
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

chat = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)

query_template = """
You are a customer at a pizza restaurant. 
You are in an ordering situation.

menu list:
Bulgogi pizza
Cheese pizza
Pepperoni pizza
Potato pizza

previous conversation:
{conversation}
now conversation
customer: 
"""
query_prompt = PromptTemplate(
    input_variables=["conversation"], template=query_template
)

query = LLMChain(
    llm=chat,
    prompt=query_prompt
)

#########

important_template = """
On the scale of 1 to 10, where 1 is purely mundane (e.g., routine morning greetings) and 10 is extremely poignant (e.g., a conversation about breaking up, a fight), rate the likely poignancy of the following conversation for {name}.

Conversation: 
{event}

Rate (return a number between 1 to 10):
"""
important_prompt = PromptTemplate(
    input_variables=["name", "event"], template=important_template
)

important_score = LLMChain(
    llm=chat,
    prompt=important_prompt
)

def call(request):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    # openai.api_key = OPENAI_API_KEY
    # openai_response = openai.ChatCompletion.create(
    #     model="gpt-3.5-turbo",
    #     messages=body["messages"]
    # )
    # openai_response_message = openai_response["choices"][0]["message"]

    all_chat_data_string = ""
    for chat_data in body["messages"]:
        if chat_data["role"] == "user":
            all_chat_data_string += "waiter" + ": " + chat_data["content"] + "\n"
            user_message = chat_data["content"]
        else:
            all_chat_data_string += chat_data["role"] + ": " + chat_data["content"] + "\n"
    
    answer = query.run(conversation = all_chat_data_string)

    conversation = Database.get_all_documents(db, "conversations", "collection")
    print(conversation)
    for i in conversation:
        continue
    node = i["node"] + 1

    id = uuid.uuid1()
    datetimeStr = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%L")

    important_str = important_score.run(event = answer, name = "User")
    important_str = "0" + important_str
    score = int(''.join(filter(str.isdigit, important_str)))

    document_user = {"_id":{ObjectId(id.hex)},"node":node,"timestamp":datetimeStr,"reflect":user_message,"name":"user","important":score}
    document_customer = {"_id":{ObjectId(id.hex)},"node":node,"timestamp":datetimeStr,"reflect":answer,"name":"customer","important":score}

    print(Database.set_document(db, "conversations", "user", document_user))
    print(Database.set_document(db, "conversations", "user", document_customer))
    messages_response = body["messages"] + [
        {
            "role": "customer",
            "content": answer
        }
    ]
    
    return JsonResponse({
        "messages": messages_response
    })