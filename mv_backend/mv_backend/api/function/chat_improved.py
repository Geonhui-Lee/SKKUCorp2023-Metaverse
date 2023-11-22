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
chat_history = ""
summary = ""
#"""
# You are a customer at a pizza restaurant. 
# You are in an ordering situation.

# menu list:
# Bulgogi pizza
# Cheese pizza
# Pepperoni pizza
# Potato pizza

persona_dict = {"Pizza Chef" : "Your name is Jake. Your job a pizza chef(Don't forget you are not a pizza worker. Do not serve a pizza. Explain about pizza)" , "Police Officer" : "Your name is Mike. Your job a police officer(Don't forget)", "Artist" : "Your name is Bob. Your job an artist(Don't forget)", "Astronaut" : "Your name is Armstrong. Your job an astronaut(Don't forget)."}

query_template = """
If the user's response is *short*, *incomplete*, *lacking in detail*, or *unclear*, you should *always* ask the user to provide more details. Any response that consists of a single or a few meaningless words should be counted as a response lacking in detail.
When encountering a user's response that is *short*, *incomplete* or *lacking in detail*, the assistant should proactively seek further clarification. This involves setting aside some aspects of the user's previous responses to focus on obtaining more comprehensive information. The assistant should employ courteous and encouraging language to invite the user to expand on their response.
- Mandatory Action: The assistant must request additional details from the user.
- Suggested Phrases: Use phrases such as 'Could you please provide more details on that?', 'I'm interested in hearing more about this. Could you elaborate?', or 'Your input is valuable. Could you expand a bit more on that point?'


You will communicate with the user as an NPC (assistant) with the {npc} job. The following is the specific personal information for the NPC you are tasked to act as.
{npc}: {persona}

Commonly, an NPC should *always* provide a *brief*, *concise* answer. Up to two or three sentences are acceptable. If the user's response is *short*, *incomplete*, *lacking in detail*, or *unclear*, you should *always* ask the user to provide more details. Any response that consists of a single or a few meaningless words should be counted as a response lacking in detail.

CEFR is the English-level criteria that ranges from A1 to C2 (pre-A1, A1, A2, B1, B2, C1, C2). Please talk to the user according to the user's English level. The user's English level is provided as a CEFR indicator.
User's CEFR level: "{user_cefr}"

User's characteristic: "{reflect}"
- induce the conversation on the topic of *your job* and *the user's interest* by referring *user's character*, *keeping concept of your job*.
- generate answer that match *the user's conversation style*.

User's bad: "{retrieve}"
- You suggest an answer the user can understand by *referring* to "User's bad".
- You should focus on a conversation about your job.

if (the user is unable to answer):
- First,*ask* the user to confirm whether the user does not understand the question.
- Then, if the user responds that he or she did not clearly understand the question, you have to *help* the user to answer(e.g suggest a user's answer, regenerate your question easily) by *using* "User's bad".

Previous conversation:
    {summary}
    {previous_conversation}
    {chat_history}

Current user conversation:
user: {user_input}
{npc}: 
foramt:
(two sentence)
""" #아이가 짧게 질문했을 때 길게 말할 수 있도록 할 것

query_prompt = PromptTemplate(
    input_variables=["chat_history", "previous_conversation", "npc", "persona", "user_cefr", "reflect", "retrieve", "user_input", "summary"], template=query_template
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

def evaluate_message(user_message):
    improved_answer_chat = CommonChatOpenAI()
    improvement_openai_client = openai()
    improvement_messages = [
        {"role": "system", "content": """
            In a number from 0 to 100, rate the user's response(s) as a score regarding the completeness, the details, and the meaning.
                - The score should be low if the user's message is too short, unclear, or lacking in detail.
                - The score should be high if the user's message is clear, detailed, and has points.

            All the assistant responses should *solely* include the score.
                - Minimum value: 0
                - Maximum value: 100
        """},
        {"role": "user", "content": str(user_message)},
    ]
    
    improvement_response = openai.ChatCompletion.create(
        model=gpt_model_name,
        messages=improvement_messages
    )
    improvement_answer = int(improvement_response["choices"][0]["message"]["content"])
    return improvement_answer

def revoke_answer_response(user_message):
    improvement_messages = [
        {"role": "system", "content": """
            If the user's response is *short*, *incomplete*, *lacking in detail*, or *unclear*, you should *always* ask the user to provide more details. Any response that consists of a single or a few meaningless words should be counted as a response lacking in detail.
            When encountering a user's response that is *short*, *incomplete* or *lacking in detail*, the assistant should proactively seek further clarification. This involves setting aside some aspects of the user's previous responses to focus on obtaining more comprehensive information. The assistant should employ courteous and encouraging language to invite the user to expand on their response.
            - Mandatory Action: The assistant must request additional details from the user.
            - Suggested Phrases: Use phrases such as 'Could you please provide more details on that?', 'I'm interested in hearing more about this. Could you elaborate?', or 'Your input is valuable. Could you expand a bit more on that point?'
        """},
        {"role": "user", "content": str(user_message)},
    ]
    
    improvement_response = openai.ChatCompletion.create(
        model=gpt_model_name,
        messages=improvement_messages
    )
    improvement_answer = improvement_response["choices"][0]["message"]["content"]
    return improvement_answer

def call(request):
    global before_opponent
    global memory_dict
    global summary
    global chat_history
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    
    user_message = body["messages"][-1]["content"]
    user_message_score = evaluate_message(user_message)
    if (user_message_score < 30):
        npc_message = revoke_answer_response(user_message)
        JsonResponse({
            "messages": npc_message
        })

    
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
        memory_dict[user_name] = ConversationSummaryBufferMemory(llm= OpenAI(), max_token_limit = 300,memory_key="chat_history", input_key= "user_input", return_messages= True)
    
    memory = memory_dict.get(user_name)
    
    LLMChainQuery = LLMChain(
        llm = chat,
        prompt = query_prompt,
        memory = memory,
        verbose = True
    )
    
    
    #대화 내용 DB에서 가져오기
    if(before_opponent != opponent):
        conversation = db.get_recent_documents(user_name, "Memory", 10)
        conversation = list(conversation)
        for session in reversed(conversation):
            if(session['name'] == user_name and session['opponent'] == opponent):
                chat_history += "User: " + session['memory'] + "\n"
            elif(session['name'] == opponent):
                chat_history +=  opponent + ": " + session['memory'] + "\n"
            elif(session['name'] == 'summary' and session['opponent'] == opponent):
                summary += session['memory']
    print(chat_history)
    
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
    reflect_data = Database.get_all_documents(db, f"{user_name}", "Reflects")

    cefr = "Pre-A1"
    retrieve = ""
    retrieve_list = list()
    reflect = ""
    reflect_list = list()

    for data in cefr_data:
        cefr = data["cefr"]
    
    for data in retrieve_data:
        retrieve_list.append(data["retrieve"])

    for data in reflect_data:
        reflect_list.append(data["reflect"])
    
    data_num = 0
    for data in reversed(retrieve_list):
        data_num += 1
        if data_num > 1:
            break
        retrieve += str(data_num) + ". " + data + "\n"
    
    data_num = 0
    for data in reversed(reflect_list):
        data_num += 1
        if data_num > 1:
            break
        reflect += str(data_num) + ". " + data + "\n"
    
    # retrieve = """
    # 1. The user does not know words such as "expand, billion".
    # 2. The user does not understand sentence structures such as "particle phrases".
    # 3. The user do not understand long sentences well.
    # """
    
    # "Reflect/Retrieve 정보를 기반으로 다음 대화에 들어갈 때 선생님이 이 아이를 정확히 인지하고 그거에 맞게 대화 세션을 어떻게 이끌어 나갈지를 설계해야 돼."
    if(cefr == "Idk"):
        cefr = "pre-A1"
    
    answer = LLMChainQuery.predict(
        npc = opponent,
        persona = persona_dict[opponent],
        user_cefr = cefr,
        reflect = reflect,
        retrieve = retrieve,
        user_input = user_message,
        previous_conversation = chat_history,
        summary = summary
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
    #improvement_openai_client = openai()
    # improvement_messages = [
    #     #{"role": "system", "content": "NPC(Assistant)가 답변을 해야하는 상황이야. NPC가 Reflect (유저 특성) 정보, Retrieve (미진사항) 정보를 기반으로 다음 대화에 들어갈 때 사용자를 정확히 인지하고 그거에 맞게 대화 세션을 어떻게 이끌어 나갈지를 설계해야 돼. 주어진 Reflect 정보, Retrieve 정보를 반영해서 기존 답변을 개선해줘."},
    #     {"role": "system", "content": "The NPC (Assistant) has to answer. NPC needs to design how to accurately recognize the user and lead the conversation session when entering the next conversation based on Reflect information and Retrieve information. Please improve the existing answer by reflecting the given Reflect information and Retrieve information."},
    #     {"role": "assistant", "content": answer},
    #     {"role": "system", "content": "[Reflect (user's characteristics) Information] " + reflect},
    #     {"role": "system", "content": "[Retrieve (improvements that the user needs to acknowledge)] " + retrieve}
    # ]
    
    # improvement_response = openai.ChatCompletion.create(
    #     model=gpt_model_name,
    #     messages=improvement_messages
    # )
    #print(improvement_response["choices"])
    #improvement_answer = improvement_response["choices"][0]["message"]["content"]
    

    messages_response = body["messages"] + [
        {
            "role": opponent,
            "content": answer, #improvement_answer, #answer
        }
    ]
    before_opponent = opponent
    
    print(memory.load_memory_variables({}))
    print(type(memory.load_memory_variables({})['chat_history'][0]) == HumanMessage)
    return JsonResponse({
        "messages": messages_response
    })