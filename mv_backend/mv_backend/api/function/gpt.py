from django.http import HttpResponse, JsonResponse
from mv_backend.lib.database import Database
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
from datetime import datetime
from bson.objectid import ObjectId

db = Database()

openai.api_key = OPENAI_API_KEY
import os
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

chat = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)

#"""
# You are a customer at a pizza restaurant. 
# You are in an ordering situation.

# menu list:
# Bulgogi pizza
# Cheese pizza
# Pepperoni pizza
# Potato pizza

query_template = """
You are a {npc} who communicates with user.
{npc}: {persona}

CEFR is the English's level criteria established by the Common European Framework of Reference for Languages, which ranges from A1 to C2 (pre A1,A1,A2,B1,B2,C1,C2).
Please talk according to the user's English level. The user's English level is provided as a CEFR indicator and the customer's CEFR is 'pre A1'.

user's CEFR: {cefr}
user's interest: {interest}

If the user does not respond, help the user respond in English.

previous conversation:
{conversation}
Current user conversation:
{current}
now answer
{npc}: 
"""

query_prompt = PromptTemplate(
    input_variables=["npc", "persona", "cefr", "interest", "conversation", "current"], template=query_template
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
    
    for chat_data in body["messages"]:
        if chat_data["role"] == "system":
            opponent = chat_data["content"]
            break
    
    user_message = body["messages"][-1]["content"]
    all_chat_data_string = ""
    # for chat_data in body["messages"]:
    #     if chat_data["role"] == "user":
    #         all_chat_data_string += "waiter" + ": " + chat_data["content"] + "\n"
    #         user_message = chat_data["content"]
    #     else:
    #         all_chat_data_string += chat_data["role"] + ": " + chat_data["content"] + "\n"

    conversation = Database.get_all_documents(db, "conversations", "user")
    
    data_num = 0
    user_message = ""
    for chat_data in conversation:
        data_num += 1
        if (chat_data["name"] == "user") or (chat_data["name"] == opponent):
            all_chat_data_string += chat_data["name"] + ": " + chat_data["memory"] + "\n"

    if data_num == 0:
        messages_response = body["messages"] + [
            {
                "role": "assistant",
                "content": "converse: " + "None"
            }
        ]

        return JsonResponse({
            "messages": messages_response
        })
    
    cefr_data = Database.get_all_documents(db, "CEFR", "user")
    persona_data = Database.get_all_documents(db, "Persona", opponent)

    cefr = ""
    interest = ""
    persona = ""
    for data in cefr_data:
        cefr = data["cefr"]
        interest = data["interest"]
    for data in persona_data:
        persona = data["persona"]

    answer = query.run(npc = opponent, persona = persona, cefr = cefr, interest = interest, conversation = all_chat_data_string, current = user_message)

    conversation = Database.get_all_documents(db, "conversations", "user")
    print(conversation)
    node = 0
    data_num = 0

    for i in conversation:
        data_num += 1
    
    if data_num != 0:
        node = i["node"] + 1
    
    datetimeStr = datetime.now().strftime("%Y-%m-%d")

    important_str = important_score.run(event = user_message, name = "User")
    important_str = "0" + important_str
    score_user = int(''.join(filter(str.isdigit, important_str)))
    if score_user == 110:
        score_user = 0
    
    important_str = important_score.run(event = opponent + ": " + answer, name = "User")
    important_str = "0" + important_str
    score_customer = int(''.join(filter(str.isdigit, important_str)))
    if score_customer == 110:
        score_customer = 0
    
    document_user = {"_id":ObjectId(),"node":node,"timestamp":datetimeStr,"memory":user_message,"name":"user","important":score_user}

    node += 1
    document_customer = {"_id":ObjectId(),"node":node,"timestamp":datetimeStr,"memory":answer,"name":opponent,"important":score_customer}

    print(Database.set_document(db, "conversations", "user", document_user))
    print(Database.set_document(db, "conversations", "user", document_customer))

    messages_response = body["messages"] + [
        {
            "role": opponent,
            "content": answer
        }
    ]
    
    return JsonResponse({
        "messages": messages_response
    })