from django.http import HttpResponse, JsonResponse
from mv_backend.lib.database import Database
from mv_backend.settings import OPENAI_API_KEY
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
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
memory = ConversationBufferMemory(memory_key="chat_history", input_key= "user_input")
chat = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)

#"""
# You are a customer at a pizza restaurant. 
# You are in an ordering situation.

# menu list:
# Bulgogi pizza
# Cheese pizza
# Pepperoni pizza
# Potato pizza

persona_dict = {"Pizza Chef" : "Your name is Jake. You're job a pizza chef(Don't forget)" , "Police Officer" : "Your name is Mike. You're job a police officer(Don't forget)", "Artist" : "Your name is Bob. You're job an artist(Don't forget)", "Astronaut" : "Your name is Armstrong. You're job an astronaut(Don't forget)"}

query_template = """
You are a {npc} who communicates with user. *Always* Answer briefly and concisely.
{npc}: {persona}

CEFR is the English's level criteria established by the Common European Framework of Reference for Languages, which ranges from A1 to C2 (pre-A1,A1,A2,B1,B2,C1,C2).
Please talk to the user according to the user's English level. The user's English level is provided as a CEFR indicator.

user's CEFR: {user_cefr}
user's interest: {interest}
user is bad at:
{retrieve}

If user is unable to answer:
    You have to *help* user generate the next answer to your last answer in English by *using* what is user bad at.
    You should *suggest* a user response along with advice to the user.

previouse conversation:
{chat_history}
Current user conversation:
{user_input}
now answer
{npc}: 
"""

query_prompt = PromptTemplate(
    input_variables=["chat_history", "npc", "persona", "user_cefr", "interest", "retrieve", "user_input"], template=query_template
)

query = LLMChain(
    llm=chat,
    prompt=query_prompt,
    memory = memory,
    verbose=True
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
        if chat_data["role"] == "npc_name":
            opponent = chat_data["content"]
            break
        
    user_name = ""
    for chat_data in body["messages"]:
        if chat_data["role"] == "user_name":
            user_name = chat_data["content"]
            break
    
    user_message = ""
    user_message = body["messages"][-1]["content"]
    all_chat_data_string = ""
    # for chat_data in body["messages"]:
    #     if chat_data["role"] == "user":
    #         all_chat_data_string += "waiter" + ": " + chat_data["content"] + "\n"
    #         user_message = chat_data["content"]
    #     else:
    #         all_chat_data_string += chat_data["role"] + ": " + chat_data["content"] + "\n"

    conversation = Database.get_all_documents(db, f"{user_name}" , "Conversations")

    before_data_num = 0
    for chat_data in conversation:
        if (chat_data["name"] == f"{user_name}" and chat_data["opponent"] == opponent) or (chat_data["name"] == opponent and chat_data["opponent"] == f"{user_name}"):
            before_data_num += 1
    
    data_num = 0
    for chat_data in conversation:
        if (chat_data["name"] == f"{user_name}" and chat_data["opponent"] == opponent) or (chat_data["name"] == opponent and chat_data["opponent"] == f"{user_name}"):
            data_num += 1
            if data_num >= before_data_num - 100:
                all_chat_data_string += chat_data["name"] + ": " + chat_data["memory"] + "\n"
    
    if data_num == 0:
        all_chat_data_string = "None"
    
    cefr_data = Database.get_all_documents(db, f"{user_name}", "CEFR")
    retrieve_data = Database.get_all_documents(db, f"{user_name}", "Retrieves")

    cefr = "pre-A1"
    interest = ""
    retrieve = ""
    retrieve_list = list()

    for data in cefr_data:
        cefr = data["cefr"]
        interest = data["interest"]
    
    for data in retrieve_data:
        retrieve_list.append(data["retrieve"])
    
    data_num = 0
    for data in reversed(retrieve_list):
        data_num += 1
        if data_num > 4:
            break
        retrieve += str(data_num) + ". " + data + "\n"
    
    
    answer = query.predict(npc = opponent, persona = persona_dict[opponent], user_cefr = cefr, interest = interest, retrieve = retrieve, user_input = user_message)

    conversation = Database.get_all_documents(db, f"{user_name}", "Conversations")
    print(conversation)
    node = 0
    data_num = 0

    for i in conversation:
        data_num += 1
    
    if data_num != 0:
        node = i["node"] + 1
    
    datetimeStr = datetime.now().strftime("%Y-%m-%d")

    important_str = important_score.run(event = user_message, name = f"{user_name}")
    important_str = "0" + important_str
    score_user = int(''.join(filter(str.isdigit, important_str)))
    if score_user > 10:
        score_user = 0
    
    important_str = important_score.run(event = opponent + ": " + answer, name = f"{user_name}")
    important_str = "0" + important_str
    score_customer = int(''.join(filter(str.isdigit, important_str)))
    if score_customer > 10:
        score_customer = 0
    
    document_user = {"_id":ObjectId(),"node":node,"timestamp":datetimeStr,"memory":user_message,"name":f"{user_name}","opponent":opponent,"important":score_user}

    node += 1
    document_customer = {"_id":ObjectId(),"node":node,"timestamp":datetimeStr,"memory":answer,"name":opponent,"opponent":f"{user_name}","important":score_customer}

    # print(Database.set_document(db, f"{user_name}" , "Conversations", document_user))
    # print(Database.set_document(db, f"{user_name}", "Conversations",  document_customer))

    messages_response = body["messages"] + [
        {
            "role": opponent,
            "content": answer
        }
    ]
    
    return JsonResponse({
        "messages": messages_response
    })