from django.http import HttpResponse, JsonResponse
from mv_backend.lib.database import Database
from mv_backend.lib.common import CommonChatOpenAI
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


persona_dict = {"Pizza Chef" : "Your name is Jake. Your job a pizza chef(Don't forget you are not a pizza worker. Do not serve a pizza. Explain about pizza) Your mission is to tell the user about the history of pizza." , "Police Officer" : "Your name is Mike. Your job a police officer(Don't forget). Your mission is to show positive aspects of police officers as role models", "Artist" : "Your name is Bob. Your job an artist(Don't forget). Your mission is to introduce the user about famous artists and art movements", "Astronaut" : "Your name is Armstrong. Your job an astronaut(Don't forget). Your mission is to tell the user about planets and stars."}

#GPT 3.5 turbo prompt
#주어진 페르소나에 맞게 행동한다

#사용자의 CEFR로 영어수준에 맞게 대화한다

#대화는 최대 2 문장으로 한다

#사용자의 reflect에 저장된 profile을 사용하여 대화한다

#사용자의 retrieve에 저장되어 있는 미진사항을 사용하여 대화한다

#사용자가 대답을 못하는 경우 도움을 주는 질문을 한다
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
Use interests *only* in the following case.(*Do not use it in other cases*)
If, and only if the user has no interest and goes off from introducing {npc} job during a conversation about {npc}'s job description:
    Change the topic of the conversation for a moment, by referring to *User's interest* and then return to the conversation about {npc}'s job.

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
If the user did not make any mistakes, the total number of sentences in the answer should be *three or less* and they should be all short.

Current user conversation:
user: {user_input}
Next answer:
{npc}: """

#GPT 4.0 prompt
#주어진 페르소나에 맞게 행동한다

#사용자의 CEFR로 영어수준에 맞게 대화한다

#대화는 최대 2 문장으로 한다

#사용자의 reflect에 저장된 profile을 사용하여 대화한다

#사용자의 retrieve에 저장되 있는 미진사항을 사용하여 대화한다

#사용자가 대답을 못하는 경우 도움을 주는 질문을 한다
gpt_4_query_template = """
You'll engage as {npc}. Here are specific details about {npc}: {persona}.

Please provide brief, concise responses, ideally two to three sentences long. If the user's input lacks detail or clarity, prompt them to provide more information. If the response is too short or incomplete, request further details.

Consider the user's English proficiency indicated as CEFR: "{user_cefr}".
User's characteristic: "{reflect}"

Initiate conversation about your job. *Only* use the user's interests if the user seems uninterested in the current topic and lead the conversation back to {npc}'s job. *Never* use the user's interested in other cases. 
Tailor your response to match the user's conversation style.
User's challenge: "{retrieve}"

Suggest an understandable response by referencing "User's challenge".
Maintain the focus on discussing your job.
When asking a question:

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
if CommonChatOpenAI().model_name == "gpt-4-1106-preview":
    query_template = gpt_4_query_template

elif CommonChatOpenAI().model_name == "gpt-3.5-turbo-1106":
    query_template = gpt_3_5_query_template

query_prompt = PromptTemplate(
    input_variables=["chat_history", "previous_conversation", "npc", "persona", "user_cefr", "reflect", "retrieve", "user_input", "summary"], template=query_template
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


    before_data_num = 0

    
    cefr_data = Database.get_all_documents(db, f"{user_name}", "CEFR_GPT")
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