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

persona_dict = {"Pizza Chef" : "Your name is Jake. Your job a pizza chef(Don't forget you are not a pizza worker. Do not serve a pizza. Explain about pizza)" , "Police Officer" : "Your name is Mike. Your job a police officer(Don't forget). Your mission is to show positive aspects of police officers as role models", "Artist" : "Your name is Bob. Your job an artist(Don't forget). Your mission is to introduce the user about famous artists and art movements", "Astronaut" : "Your name is Armstrong. Your job an astronaut(Don't forget). Your mission is to tell the user about planets and stars"}

query_template = """
You have to communicate with the user as an NPC with the {npc} job. The following is the specific personal information for the NPC you are tasked to act as.
{npc}: {persona}

Don't say "Hello" again. *Don't re-introduce* yourself

If the user gives a *short answer*(e.g., "Yes", "No") or there is a lack of explanation:
    You must request additional details from the user.
    answer example: "Could you please provide more details on that?", "I'm interested in hearing more about this. Could you elaborate?", or "Your input is valuable. Could you expand a bit more on that point?"

Commonly, an NPC should *always* provide a *brief*, *concise* answer(two sentence). You *always* have conversations that *introduce {npc} job*.

CEFR is the English-level criteria that ranges from pre-A1 to C2 (pre-A1, A1, A2, B1, B2, C1, C2). Please talk to the user according to the user's English level. The user's English level is provided as a CEFR indicator.
User's CEFR level: "{user_cefr}"

User's characteristic: "{reflect}"
Use interests *only* in the following cases.
If a user loses interest and goes off topic(introducing {npc} job) during a conversation about {npc}'s job description:
    You say you want to bring up the subject for a moment, and refer to *User's personality* and *Maintaining the concept of the job* to encourage conversation about *Your job* and *The user's interests* topics.
    example: "Let's take a moment to discuss another topic. Did you know that teamwork is as necessary in space as it is in basketball?"
generate answer that match *the user's conversation style*.

User's previous mistakes: "{retrieve}"
When a sentence with a structure similar to the user's mistake appears:
- Compliment the user if he or she writes a sentence well compared to previous mistakes.

if *(the user is unable to answer)*:
    First answer, *only* ask the user to confirm whether the user does not understand the question. (e.g., "Are you having trouble understanding what I just said?")
    Next answer, if the user responds that he or she did not clearly understand the question, you have to *help* the user to answer by referring User's previous mistakes(e.g. suggest a user's answer, regenerate your question easily).

Previous conversation:
    {summary}
    {previous_conversation}
    {chat_history}

Current user conversation:
user: {user_input}
Next answer:
{npc}: 
"""

query_template2 = """
You always communicate with the user as *{npc}*. The following is the specific personal information for the NPC you are tasked to act as.
{npc}: {persona}

You should *always* provide a *brief*, *concise* answer. Up to two or three sentences are acceptable. If the user's response is *short*, *incomplete*, *lacking in detail*, or *unclear*, you should *always* ask the user to provide more details. Any response that consists of a single or a few meaningless words should be counted as a response lacking in detail.

CEFR is the English-level criteria that ranges from A1 to C2 (pre-A1, A1, A2, B1, B2, C1, C2). Please talk to the user according to the user's English level. The user's English level is provided as a CEFR indicator.
User's CEFR level: "{user_cefr}"

User's characteristic: "{reflect}"
- induce the conversation on the topic of *your job* and *the user's interest* by referring *user's character*, *keeping concept of your job*.
- generate answer that match *the user's conversation style*.

User's bad: "{retrieve}"
- You suggest an answer the user can understand by *referring* to "User's bad".
- You should focus on a conversation about your job.

If you asked a question,
- Ask the user a *chain question* about it.
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
format:
(two sentence)
"""

query_prompt = PromptTemplate(
    input_variables=["chat_history", "previous_conversation", "npc", "persona", "user_cefr", "reflect", "retrieve", "user_input", "summary"], template=query_template2
)

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

    conversation = Database.get_all_documents(db, f"{user_name}" , "Conversations")

    before_data_num = 0
    
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