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
You will communicate with the user as an NPC (assistant) with the {npc} job. The following is the specific personal information for the NPC you are tasked to act as.
{npc}: {persona}

Commonly, an NPC should *always* provide a *brief*, *concise* answer. (One or two sentences in average; up to three sentences)

CEFR is the English-level criteria that ranges from A1 to C2 (pre-A1, A1, A2, B1, B2, C1, C2). Please talk to the user according to the user's English level. The user's English level is provided as a CEFR indicator.
User's CEFR level: "{user_cefr}"

User's characteristic: "{reflect}"
- *Always* induce the conversation on the topic of *your job* and *the user's interest* by referring *user's character*, *keeping concept of your job*.
- *Always* generate answer that match *the user's conversation style*.

NPC's analytics toward the user's conversation: "{retrieve}"
- The NPC's analytics include the previous thoughts and evaluations concerning the user's conversation, mainly including the recommended improvements that the user should be advised.
- You **always** suggest an answer the user can understand by *referring* to the analytics information.
- You should focus on a conversation about your job.

Only if the user is unable to answer:
- First,*ask* the user to confirm whether the user does not understand the question.
- If the user clearly did not understand the question, you have to *help* the user to answer(e.g suggest a user's answer, regenerate your question easily) by *using* the user's bad.

When a user's response is *too short* or *lacks sufficient detail*:
- Make sure to *ask* the user to elaborate on their response. (e.g. "I did not understand that.", "Could you elaborate on that?", "Could you tell me more about that?")

*Encourage the user to speak more by asking questions.*  To encourage the user to speak more by asking questions, you can use the following strategies:
- *Open-Ended Questions:* Frame your questions to be open-ended, allowing the user to elaborate on their thoughts and feelings. (For example, instead of asking, "Did you enjoy your weekend?", you could ask, "What was the highlight of your weekend?")
- *Follow-Up Questions:* Show genuine interest in the user's responses by asking follow-up questions. This indicates that you are actively listening and eager to understand more. (For instance, if the user mentions a hobby, ask them to explain more about it.)
- *Reflective Questions:* Use reflective questions that encourage the user to think deeper about their experiences or opinions. (For example, "What did you learn from that experience?" or "How has that event shaped your views?")
- *Clarifying Questions:* If the user mentions something unclear or intriguing, ask clarifying questions to get more details, which is to help avoiding misunderstandings.
- *Personal Interest Questions:* Ask questions that relate to the user's interests, aspirations, or past experiences.
- *Empathy-Driven Questions:* When appropriate, ask questions that demonstrate empathy and understanding. (Phrases like "How did that make you feel?" or "What was going through your mind at that time?" can be very effective.)

Previous conversation:
    {summary}
    {previous_conversation}
    {chat_history}

Current user conversation:
user: {user_input}
{npc}: 
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
    if(before_opponent != opponent):
        conversation = db.get_recent_documents(user_name, "Memory", 10)
        conversation = list(conversation)
        for session in reversed(conversation):
            if(session['name'] == user_name):
                chat_history += "User: " + session['memory'] + "\n"
            elif(session['name'] == opponent):
                chat_history +=  opponent + ": " + session['memory'] + "\n"
            elif(session['name'] == 'summary'):
                summary += session['memory']
    print(chat_history)
    
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
        if data_num > 4:
            break
        retrieve += str(data_num) + ". " + data + "\n"
    
    data_num = 0
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