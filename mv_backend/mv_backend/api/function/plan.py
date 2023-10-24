from django.http import HttpResponse, JsonResponse
from mv_backend.settings import OPENAI_API_KEY
import json, openai
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
import numpy as np
from numpy.linalg import norm
from langchain.embeddings import OpenAIEmbeddings
import datetime
import time

openai.api_key = OPENAI_API_KEY
import os
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

chat = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)

wrong_plan_template = """
Your objective is to make 5 breif but detailed plans based on the given information to allow the user to improve their english or their part time service this could also include recommending a specific menu the next time the customer comes. Make sure to give a reasoning of why you made this plan and which retireve and reflect data the plan was based on.
If the user made a mistake in their english language or grammar, make one of the plans as take note of what gramatic mistakes were made.
previously the user made the mistake of {retrieve}. The reflection data will mainly store the types of food a specific customer likes or dislikes. Here is the reflect data {reflect}.
"""
wrong_plan_prompt = PromptTemplate(
    input_variables=["retrieve", "reflect"], template= wrong_plan_template
)

wrong_plan = LLMChain(
    llm=chat,
    prompt=wrong_plan_prompt
)

important = 0
all_chat_data = ""

def call(request):

    # declare for start
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    
    messages_response = body["messages"] + [
        {
            "role": "assistant",
            "content": "plan: " + wrong_plan.run(retrieve = "", reflect = "")
        }
    ]

    return JsonResponse({
        "messages": messages_response
    })