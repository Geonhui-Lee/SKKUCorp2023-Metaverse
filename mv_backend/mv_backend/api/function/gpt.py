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

query_template = """
You are a customer at a pizza restaurant. Have a conversation appropriate to the situation, such as when you order a pizza.

previuos conversation:
{conversation}
"""
query_prompt = PromptTemplate(
    input_variables=["conversation"], template=query_template
)

query = LLMChain(
    llm=chat,
    prompt=query_prompt
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
        data_num += 1
        if data_num > 10:
            break
        if chat_data["role"] == "user":
            all_chat_data_string += "waiter" + ": " + chat_data["content"] + "\n"
        else:
            all_chat_data_string += chat_data["role"] + ": " + chat_data["content"] + "\n"
    messages_response = body["messages"] + [
        {
            "role": "customer",
            "content": query.run(conversation = all_chat_data_string)
        }
    ]
    
    return JsonResponse({
        "messages": messages_response
    })