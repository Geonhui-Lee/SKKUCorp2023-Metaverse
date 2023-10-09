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


plan_template = """
{customer} came in. Here is {name}'s retrieved data {retrieve}. Here is also {name}'s previous reflection that {name}'s made {reflect}. Based on these data make a plan on how to treat the customer {customer} (e.g., retrieve: Tim did not like ketchup, reflect: I will not serve ketchup next time, plan: Don't serve ketchup to tim because he doesn't like ketchup)
Today is {time}. Here is {name}'s plan today in broad-strokes (with the time of the day. e.g., have a lunch at 12:00 pm, watch TV from 7 to 8 pm): 1) wake up and complete the morning routine at {wake_up}, 2)
"""
plan_prompt = PromptTemplate(
    input_variables=["customer", "name", "retrieve", "reflect"], template= plan_template
)

plan = LLMChain(
    llm=chat,
    prompt=plan_prompt
)

# every prompts for this code

# generate the query score
# !<INPUT 2>! -- Reverie date time now
# !<INPUT 3>! -- Persona first names
# !<INPUT 4>! -- wake_up_hour
daily_plan_template = """
Today is {time}. Here is {name}'s plan today in broad-strokes (with the time of the day. e.g., have a lunch at 12:00 pm, watch TV from 7 to 8 pm): 1) wake up and complete the morning routine at {wake_up}, 2)
"""
daily_plan_prompt = PromptTemplate(
    input_variables=["time", "name", "wake_up"], template=daily_plan_template
)

daily_plan = LLMChain(
    llm=chat,
    prompt=daily_plan_prompt
)

# Variables: 
# !<INPUT 0>! -- Schedule format
# !<INPUT 1>! -- Commonset
# !<INPUT 2>! -- prior_schedule
# !<INPUT 3>! -- intermission_str
# !<INPUT 4>! -- intermission 2
# !<INPUT 5>! -- prompt_ending

hourly_plan_template = """
Hourly schedule format: 
{hourly_format}
===
{prior_schedule}
"""
hourly_plan_prompt = PromptTemplate(
    input_variables=["hourly_format", "prior_schedule"], template=hourly_plan_template
)

hourly_plan = LLMChain(
    llm=chat,
    prompt=hourly_plan_prompt
)
# Variables: 
# !<INPUT 0>! -- Commonset
# !<INPUT 1>! -- Surrounding schedule description
# !<INPUT 2>! -- Persona first name
# !<INPUT 3>! -- Persona first name
# !<INPUT 4>! -- Current action
# !<INPUT 5>! -- curr time range
# !<INPUT 6>! -- Current action duration in min
# !<INPUT 7>! -- Persona first names

decomp_task_template = """
Describe subtasks in 5 min increments. 
---
Name: Kelly Bronson
Age: 35
Backstory: Kelly always wanted to be a teacher, and now she teaches kindergarten. During the week, she dedicates herself to her students, but on the weekends, she likes to try out new restaurants and hang out with friends. She is very warm and friendly, and loves caring for others.
Personality: sweet, gentle, meticulous
Location: Kelly is in an older condo that has the following areas: {kitchen, bedroom, dining, porch, office, bathroom, living room, hallway}.
Currently: Kelly is a teacher during the school year. She teaches at the school but works on lesson plans at home. She is currently living alone in a single bedroom condo.
Daily plan requirement: Kelly is planning to teach during the morning and work from home in the afternoon.s

Today is Saturday May 10. From 08:00am ~09:00am, Kelly is planning on having breakfast, from 09:00am ~ 12:00pm, Kelly is planning on working on the next day's kindergarten lesson plan, and from 12:00 ~ 13pm, Kelly is planning on taking a break. 
In 5 min increments, list the subtasks Kelly does when Kelly is working on the next day's kindergarten lesson plan from 09:00am ~ 12:00pm (total duration in minutes: 180):
1) Kelly is reviewing the kindergarten curriculum standards. (duration in minutes: 15, minutes left: 165)
2) Kelly is brainstorming ideas for the lesson. (duration in minutes: 30, minutes left: 135)
3) Kelly is creating the lesson plan. (duration in minutes: 30, minutes left: 105)
4) Kelly is creating materials for the lesson. (duration in minutes: 30, minutes left: 75)
5) Kelly is taking a break. (duration in minutes: 15, minutes left: 60)
6) Kelly is reviewing the lesson plan. (duration in minutes: 30, minutes left: 30)
7) Kelly is making final changes to the lesson plan. (duration in minutes: 15, minutes left: 15)
8) Kelly is printing the lesson plan. (duration in minutes: 10, minutes left: 5)
9) Kelly is putting the lesson plan in her bag. (duration in minutes: 5, minutes left: 0)
---
In 5 min increments, list the subtasks {name} does when {name} is {action} from {current_time} (total duration in minutes {duration_time}): 
1) {name} is
"""

decomp_task_prompt = PromptTemplate(
    input_variables=["name", "action", "current_time","duration_time"], template=decomp_task_template
)

decomp_task = LLMChain(
    llm=chat,
    prompt=decomp_task_prompt
)

important = 0
all_chat_data = ""

def call(request):

    # declare for start
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    now = time.localtime()
    plan = plan.run(customer = "Bob", name = "Kim", retrieve = "Bob did not like Chicken.", reflect = "I will recommend beef instead of chicken next time.")

    hour_str = ["00:00 AM", "01:00 AM", "02:00 AM", "03:00 AM", "04:00 AM", 
                "05:00 AM", "06:00 AM", "07:00 AM", "08:00 AM", "09:00 AM", 
                "10:00 AM", "11:00 AM", "12:00 PM", "01:00 PM", "02:00 PM", 
                "03:00 PM", "04:00 PM", "05:00 PM", "06:00 PM", "07:00 PM",
                "08:00 PM", "09:00 PM", "10:00 PM", "11:00 PM"]
    n_m1_activity = []
    diversity_repeat_count = 3
    for i in range(diversity_repeat_count): 
        n_m1_activity_set = set(n_m1_activity)
        if len(n_m1_activity_set) < 5: 
            n_m1_activity = []
            for count, curr_hour_str in enumerate(hour_str): 
                if wake_up_hour > 0: 
                    n_m1_activity += ["sleeping"]
                    wake_up_hour -= 1
                else: 
                    n_m1_activity += [hourly_plan.run(
                                    hourly_plan = "1) woke up and completed the morning routine at 7:00 am, [. . . ] 6) got ready to sleep around 10 pm.", prior_schedule = plan)[0]]
    
    
    # Step 1. Compressing the hourly schedule to the following format: 
    # The integer indicates the number of hours. They should add up to 24. 
    # [['sleeping', 6], ['waking up and starting her morning routine', 1], 
    # ['eating breakfast', 1], ['getting ready for the day', 1], 
    # ['working on her painting', 2], ['taking a break', 1], 
    # ['having lunch', 1], ['working on her painting', 3], 
    # ['taking a break', 2], ['working on her painting', 2], 
    # ['relaxing and watching TV', 1], ['going to bed', 1], ['sleeping', 2]]
    _n_m1_hourly_compressed = []
    prev = None 
    prev_count = 0
    for i in n_m1_activity: 
        if i != prev:
            prev_count = 1 
            _n_m1_hourly_compressed += [[i, prev_count]]
            prev = i
        else: 
            if _n_m1_hourly_compressed: 
                _n_m1_hourly_compressed[-1][1] += 1   

    plan_decomp = decomp_task.run() 
    
    messages_response = body["messages"] + [
        {
            "role": "assistant",
            "content": "plan: " + plan
        }
    ]+ [
        {
            "role": "assistant",
            "content": "hourly plan: " + hourly_plan
        }
    ]

    return JsonResponse({
        "messages": messages_response
    })