from django.http import HttpResponse, JsonResponse
from mv_backend.lib.database import Database
from mv_backend.lib.common import CommonChatOpenAI, gpt_model_name
from mv_backend.settings import OPENAI_API_KEY
from langchain.chains import LLMChain
from langchain.memory import ConversationSummaryBufferMemory
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
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

memory_dict = dict()
chat = CommonChatOpenAI()
before_opponent = ""
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
user's Character: {reflect}
user is bad at: {retrieve}
you **always** *suggest* a user answer that the user can understand by *referring* *user's bad*.   


If user is unable to answer:
    *Ask* the user if they don't understand the question, and if so, You have to *suggest* a user answer along with advice to the user by *using* user's bad.

previouse conversation:
{chat_history}
Current user conversation:
{user_input}
now answer
{npc}: 
"""

query_prompt = PromptTemplate(
    input_variables=["chat_history", "npc", "persona", "user_cefr", "reflect", "retrieve", "user_input"], template=query_template
)

#########

# important_template = """
# On the scale of 1 to 10, where 1 is purely mundane (e.g., routine morning greetings) and 10 is extremely poignant (e.g., a conversation about breaking up, a fight), rate the likely poignancy of the following conversation for {name}.

# Conversation: 
# {event}

# Rate (return a number between 1 to 10):
# """
# important_prompt = PromptTemplate(
#     input_variables=["name", "event"], template=important_template
# )

# important_score = LLMChain(
#     llm=chat,
#     prompt=important_prompt
# )

def call(request):
    global before_opponent
    global memory_dict
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    
    for chat_data in body["messages"]:
        if chat_data["role"] == "npc_name":
            opponent = chat_data["content"]
            break
        
    user_name = ""
    for chat_data in body["messages"]:
        if chat_data["role"] == "user_name":
            user_name = chat_data["content"]
            break
        
    if user_name not in memory_dict:
        memory_dict[user_name] = ConversationSummaryBufferMemory(llm= OpenAI(), max_token_limit = 500,memory_key="chat_history", input_key= "user_input")
    
    memory = memory_dict.get(user_name)
    
    LLMChainQuery = LLMChain(
        llm = chat,
        prompt = query_prompt,
        memory = memory,
        verbose = True
    )
    
    user_message = body["messages"][-1]["content"]
    all_chat_data_string = ""
    for chat_data in body["messages"]:
        if chat_data["role"] == "user":
            all_chat_data_string += f"{user_name}" + ": " + chat_data["content"] + "\n"
            user_message = chat_data["content"]
        elif chat_data["role"] == f"{opponent}":
            all_chat_data_string += f"{opponent}" + ": " + chat_data["content"] + "\n"

    conversation = Database.get_all_documents(db, f"{user_name}" , "Conversations")

    before_data_num = 0
    # for chat_data in conversation:
    #     if (chat_data["name"] == f"{user_name}" and chat_data["opponent"] == opponent) or (chat_data["name"] == opponent and chat_data["opponent"] == f"{user_name}"):
    #         before_data_num += 1
    
    # data_num = 0
    # for chat_data in conversation:
    #     if (chat_data["name"] == f"{user_name}" and chat_data["opponent"] == opponent) or (chat_data["name"] == opponent and chat_data["opponent"] == f"{user_name}"):
    #         data_num += 1
    #         if data_num >= before_data_num - 100:
    #             all_chat_data_string += chat_data["name"] + ": " + chat_data["memory"] + "\n"
    
    # if data_num == 0:
    #     all_chat_data_string = "None"
    
    cefr_data = Database.get_all_documents(db, f"{user_name}", "CEFR")
    retrieve_data = Database.get_all_documents(db, f"{user_name}", "Retrieves")
    reflect_data = Database.get_all_documents(db, f"{user_name}", "Retrieves")

    cefr = "Pre-A1"
    interest = ""
    retrieve = ""
    retrieve_list = list()
    reflect = ""
    reflect_list = list()

    for data in cefr_data:
        cefr = data["cefr"]
    
    for data in retrieve_data:
        retrieve_list.append(data["retrieve"])

    for data in reflect_list:
        reflect_list.append(data['reflect'])
    
    data_num = 0
    for data in reversed(retrieve_list):
        data_num += 1
        if data_num > 4:
            break
        retrieve += str(data_num) + ". " + data + "\n"

    for data in reversed(reflect_list):
        data_num += 1
        if data_num > 4:
            break
        reflect += str(data_num) + ". " + data + "\n"
    
    # retrieve = """
    # 1. The user does not know words such as "expand, billion".
    # 2. The user does not understand sentence structures such as "particle phrases".
    # 3. The user do not understand long sentences well.
    # """
    
    # "Reflect/Retrieve 정보를 기반으로 다음 대화에 들어갈 때 선생님이 이 아이를 정확히 인지하고 그거에 맞게 대화 세션을 어떻게 이끌어 나갈지를 설계해야 돼."
    answer = LLMChainQuery.predict(
        npc = opponent,
        persona = persona_dict[opponent],
        user_cefr = cefr,
        reflect = reflect,
        retrieve = retrieve,
        user_input = user_message,
    )

    #conversation = Database.get_all_documents(db, f"{user_name}", "Conversations")
    
    # #print(conversation)
    # #node = 0
    # #data_num = 0

    # for i in conversation:
    #     data_num += 1
    
    # if data_num != 0:
    #     node = i["node"] + 1
    
    # datetimeStr = datetime.now().strftime("%Y-%m-%d")

    # important_str = important_score.run(event = user_message, name = f"{user_name}")
    # important_str = "0" + important_str
    # score_user = int(''.join(filter(str.isdigit, important_str)))
    # if score_user > 10:
    #     score_user = 0
    
    # important_str = important_score.run(event = opponent + ": " + answer, name = f"{user_name}")
    # important_str = "0" + important_str
    # score_customer = int(''.join(filter(str.isdigit, important_str)))
    # if score_customer > 10:
    #     score_customer = 0
    
    # document_user = {"_id":ObjectId(),"node":node,"timestamp":datetimeStr,"memory":user_message,"name":f"{user_name}","opponent":opponent,"important":score_user}
    #document_user = {"_id":ObjectId(),"node":node,"timestamp":datetimeStr,"memory":user_message,"name":f"{user_name}","opponent":opponent}
    #node += 1
    # document_customer = {"_id":ObjectId(),"node":node,"timestamp":datetimeStr,"memory":answer,"name":opponent,"opponent":f"{user_name}","important":score_customer}
    # document_customer = {"_id":ObjectId(),"node":node,"timestamp":datetimeStr,"memory":answer,"name":opponent,"opponent":f"{user_name}"}
    # print(Database.set_document(db, f"{user_name}" , "Conversations", document_user))
    # print(Database.set_document(db, f"{user_name}", "Conversations",  document_customer))

    #improved_answer_chat = CommonChatOpenAI()
    improvement_openai_client = OpenAI()
    improvement_messages = [
        {"role": "system", "content": "NPC(Assistant)가 답변을 해야하는 상황이야. NPC가 Reflect (유저 특성) 정보, Retrieve (미진사항) 정보를 기반으로 다음 대화에 들어갈 때 사용자를 정확히 인지하고 그거에 맞게 대화 세션을 어떻게 이끌어 나갈지를 설계해야 돼. 주어진 Reflect 정보, Retrieve 정보를 반영해서 기존 답변을 개선해줘."},
        {"role": "assistant", "content": answer},
        {"role": "system", "content": "[Reflect (유저 특성) 정보]" + reflect},
        {"role": "system", "content": "[Retrieve (미진 사항) 정보]" + retrieve}
    ]
    improvement_response = improvement_openai_client.chat.completions.create(
        model=gpt_model_name,
        messages=improvement_messages
    )
    improvement_answer = improvement_response["choices"][0]["text"]

    messages_response = body["messages"] + [
        {
            "role": opponent,
            "content": improvement_answer, #answer
        }
    ]
    before_opponent = opponent
    
    return JsonResponse({
        "messages": messages_response
    })