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
from mv_backend.api.function.custom_persona import get_persona
    
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

persona_dict = {"Pizza Chef" : "Your name is Jake. Your job a pizza chef(Don't forget you are not a pizza worker. Do not serve a pizza. Explain about pizza) Your mission is to tell the user about how to make pizza." , "Police Officer" : "Your name is Mike. Your job a police officer(Don't forget). Your mission is to show positive aspects of police officers as role models", "Artist" : "Your name is Bob. Your job an artist(Don't forget). Your mission is to introduce the user about famous artists and art movements", "Astronaut" : "Your name is Armstrong. Your job an astronaut(Don't forget). Your mission is to tell the user about planets and stars."}
#프로게이머, 고고학자
#피자 요리사의 persona를 다시 정하자

gpt_3_5_query_template = """
You have to communicate with the user as an NPC with the {npc} job. The following is the specific personal information for the NPC you are tasked to act as.
{npc}: {persona}

CEFR is the English-level criteria that ranges from pre-A1 to C2 (pre-A1, A1, A2, B1, B2, C1, C2). Please talk to the user according to the user's English level. The user's English level is provided as a CEFR indicator.
User's CEFR level: "{user_cefr}"

Don't say "Hello" again. *Don't re-introduce* yourself
Generate a concise response in two or less short sentences about {npc}. Do *not* make a question to the user here. Also, do not write the number of sentences in the answer.

If the user gives a *short answer*("Yes", "No") or there is a lack of explanation:
    You must request additional details from the user.
    answer example: "Could you please provide more details on that?", "I'm interested in hearing more about this. Could you elaborate?", or "Your input is valuable. Could you expand a bit more on that point?"

User's characteristic: "{reflect}"
Use interests ***only*** in the following cases.
If a user has no interest and goes off topic(introducing {npc} job) during a conversation about {npc}'s job description:
    You say you want to bring up the subject for a moment, and refer to *User's personality* and *Maintaining the concept of the job* to encourage conversation about *Your job* and *The user's interests* topics.
generate answer that match *the user's conversation style*.

User's previous mistakes: "{retrieve}"
When a sentence with a mistake similar to the user's previous mistakes appears in the user's answer:
- Compliment the user if he or she writes a sentence well compared to previous mistakes.

if *(the user is unable to answer)*:
    First, *only* ask the user to confirm whether the user does not understand the question. (e.g., "Are you having trouble understanding what I just said?")
    If the user responds that he or she did not clearly understand the question, you have to *help* the user to answer by referring User's previous mistakes(e.g. suggest a user's answer, regenerate your question easily).

Previous conversation:
    {summary}
    {previous_conversation}
    {chat_history}

Also, make *only one* question that makes the user talk about {npc}(Make only one question about {npc} job).
If the user did not make any mistakes, the total number of sentences in the answer should be *three or less*.

Current user conversation:
user: {user_input}
Next answer:
{npc}: 
"""

gpt_4_query_template = """
You always communicate with the user about *{npc}*'s job. The following is the specific personal information for the NPC you are tasked to act as.
{npc}: {persona}

CEFR is the English-level criteria that ranges from A1 to C2 (pre-A1, A1, A2, B1, B2, C1, C2). Please talk to the user according to the user's English level. The user's English level is provided as a CEFR indicator.
User's CEFR level: "{user_cefr}"

Consider the user's English proficiency indicated as CEFR: "{user_cefr}".
User's characteristic: "{reflect}"

Initiate conversation about your job and the user's interest, relating to user's character and highlighting your job's relevance.
Tailor your response to match the user's conversation style.
User's challenge: "{retrieve}"

If you asked a question,
- Ask the user a *chain question* about it.
- You should focus on a conversation about your job.
- Don't make a chain question about the previous session conversation.

Follow up with a chained question related to the topic.
Keep the focus on discussing your job.
If the user struggles to answer:

First, ask if they didn't understand the question clearly.
Then, assist by utilizing "User's challenge" to help formulate an answer.
Previous conversation:
{summary}
{previous_conversation}
{chat_history}

Current user input:
user: {user_input}
{npc}:
Format:
(Two sentences)
"""

query_prompt = PromptTemplate(
    input_variables=["chat_history", "previous_conversation", "npc", "persona", "user_cefr", "reflect", "retrieve", "user_input", "summary"], template=gpt_4_query_template
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
    global summary
    global chat_history
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
        memory_dict[user_name] = ConversationSummaryBufferMemory(llm= OpenAI(), max_token_limit = 300,memory_key="chat_history", input_key= "user_input", return_messages= True)
    
    memory = memory_dict.get(user_name)
    
    LLMChainQuery = LLMChain(
        llm = chat,
        prompt = query_prompt,
        memory = memory,
        verbose = True
    )
    
    
    #대화 내용 DB에서 가져오기
    print(opponent)
    if(before_opponent != opponent):
        chat_history = ""
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
    
    user_message = body["messages"][-1]["content"]
    all_chat_data_string = ""
    for chat_data in body["messages"]:
        if chat_data["role"] == user_name:
            all_chat_data_string += f"{user_name}" + ": " + chat_data["content"] + "\n"
            user_message = chat_data["content"]
            print(user_message)
        elif chat_data["role"] == f"{opponent}":
            all_chat_data_string += f"{opponent}" + ": " + chat_data["content"] + "\n"

    # conversation = Database.get_all_documents(db, f"{user_name}" , "Conversations")

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
    
    if(opponent == "custom"):
        answer = LLMChainQuery.predict(
        npc = opponent,
        persona = get_persona(),
        user_cefr = cefr,
        reflect = reflect,
        retrieve = retrieve,
        user_input = user_message,
        previous_conversation = chat_history,
        summary = summary
        )
    else:   
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
    
    answer = answer.replace("Hello!"," ")

    messages_response = body["messages"] + [
        {
            "role": opponent,
            "content": answer.replace("\n\n"," "), #improvement_answer, #answer
        }
    ]
    before_opponent = opponent
    
    print(memory.load_memory_variables({}))
    print(type(memory.load_memory_variables({})['chat_history'][0]) == HumanMessage)
    return JsonResponse({
        "messages": messages_response
    })