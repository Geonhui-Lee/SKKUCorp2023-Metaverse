from django.http import HttpResponse, JsonResponse
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

openai.api_key = OPENAI_API_KEY
import os
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

chat = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)

find_query_template = """
Search the pizza menu that the customer ordered.

menu list:
Bulgogi pizza
Cheeze pizza
Pepperoni pizza
Potato pizza

ordering conversation:
{conversation}

format Pizza ordered and number:["Bulgogi pizza": 0, "Cheeze pizza": 0, "Pepperoni pizza": 0, "Potato pizza": 0]
Pizza ordered and number:
"""
find_query_prompt = PromptTemplate(
    input_variables=["conversation"], template=find_query_template
)

find_query = LLMChain(
    llm=chat,
    prompt=find_query_prompt
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
    data_num = 0
    all_chat_data_string = ""
    for chat_data in body["messages"]:
        data_num += 1
        if data_num > 10:
            break
        if chat_data["role"] == "user":
            all_chat_data_string += "waiter" + ": " + chat_data["content"] + "\n"
        else:
            all_chat_data_string += chat_data["role"] + ": " + chat_data["content"] + "\n"
    
    menu = list(find_query.run(conversation = all_chat_data_string))
    menu[0] = '{'
    menu[-1] = '}'
    menu_string = "".join(menu)
    menu_dict = eval(menu_string)
    return JsonResponse(
        menu_dict
    )