from django.http import HttpResponse, JsonResponse
import json, openai
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
import numpy as np
from numpy.linalg import norm
from langchain.embeddings import OpenAIEmbeddings
import json, openai
from datetime import datetime
from bson.objectid import ObjectId
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from mv_backend.lib.database import Database

OPENAI_API_KEY = "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"
openai.api_key = OPENAI_API_KEY
import os
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

MONGODB_CONNECTION_STRING = "mongodb+srv://geonhui:dotgeon@metaverse.px60xor.mongodb.net/?"

db = Database()

chat = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)
# every agents for this code
embeddings_model = OpenAIEmbeddings()

###
generate_important_template = """
Find five important dialogues in the following conversation for {name}.

Conversation: 
{event}

Ranking:
[1]"""
generate_important_prompt = PromptTemplate(
    input_variables=["event", "name"], template=generate_important_template
)

generate_important = LLMChain(
    llm=chat,
    prompt=generate_important_prompt
)

# find the insight
# !<INPUT 0>! -- Numbered list of event/thought statements
# !<INPUT 1>! -- target persona name or "the conversation"
generate_template = """
Query:
{query}
Input:
{event}

What 1 answer to the query can {name} infer from the above statements? (example format: insight (because of 1, 5, 3))
1.
"""
generate_prompt = PromptTemplate(
    input_variables=["query", "name", "event"], template=generate_template
)

generate_retrieve = LLMChain(
    llm=chat,
    prompt=generate_prompt
)

def retrieve(npc, user):

    ### mongoDB user's memory ###
    conversation = db.get_recent_documents(user, "conversations")
    data_num = 0

    all_chat_data = []
    all_chat_data_node = []
    all_chat_data_string = ""
    for chat_data in conversation:
        data_num += 1
        all_chat_data.append(chat_data["name"] + ": " + chat_data['memory'])
        all_chat_data_node.append("[" + str(data_num) + "]" + chat_data["name"] + ": " + chat_data)
        # all_chat_data.append(chat_data)
        all_chat_data_string += chat_data["name"] + ": " + chat_data['memory'] + "\n"
    
    if data_num == 0:
        return

    # conversation = Database.get_all_documents(db, user, "conversations")
    # data_num = 0

    # all_chat_data = []
    # before_chat_data = []
    # all_chat_data_node = []
    # important = []
    # important_sum = 0
    # for chat_data in conversation:
    #     data_num += 1
    #     before_chat_data.append(chat_data["name"] + ": " + chat_data["memory"])
    #     # important.append(int(chat_data["important"]))
    
    # # data_num = 0
    # # for chat_data in reversed(important):
    # #     data_num += 1
    # #     important_sum += chat_data
    # #     if data_num > 50:
    # #         break
    
    # # if data_num == 0 or important_sum < 50:
    # #     return
    
    # if data_num == 0:
    #     return

    # important_sum = 0
    # data_num = 0
    # for chat_data in reversed(before_chat_data):
    #     data_num += 1
    #     if data_num > 100:
    #         break
    #     all_chat_data_node.append("[" + str(data_num) + "]" + chat_data)
    #     all_chat_data.append(chat_data)
    # # all_chat_data_string = ""
    # # # now reflect with 100 message data (we wil generate only one query)
    # # data_num = 0
    # # for chat_data in reversed(body["messages"]):
    # #     data_num += 1
    # #     if data_num > 100:
    # #         break
    # #     all_chat_data_node.append("[" + str(data_num) + "]" + chat_data["role"] + ": " + chat_data["content"])
    # #     all_chat_data.append(chat_data["role"] + ": " + chat_data["content"])
    # #     all_chat_data_string += chat_data["role"] + ": " + chat_data["content"] + "\n"
    

    focal_points = "Find out what the user is bad at (grammar, understanding of context, etc.)"
    embedded_query = embeddings_model.embed_query(focal_points)
    embedings = embeddings_model.embed_documents(all_chat_data_string)

    cosine = np.dot(embedings, embedded_query)/(norm(embedings, axis=1)*norm(embedded_query))
    print(cosine)

    chat_data_score = dict(zip(all_chat_data_node, cosine))

    # retrieve to find 30 chat data with the generated query, embedding vetors, recency
    data_num = 0
    recency = 1
    # for score, chat_data in zip(reversed(important), all_chat_data):
    for chat_data in all_chat_data:
        data_num += 1
        if data_num > 100:
            break
        recency *= 0.995
        
        # chat_data_score["[" + str(data_num) + "]" + chat_data] += 0.1*score + recency
        chat_data_score["[" + str(data_num) + "]" + chat_data] += recency
    
    sorted_dict = sorted(chat_data_score.items(), key = lambda item: item[1], reverse = True)
    print(sorted_dict)

    # find the insights with 30 important data
    important_data_string = "[1] "
    important_data_string += generate_important.run(name = user, event = all_chat_data_string)
    data_num = 0
    for chat_data in sorted_dict:
        data_num += 1
        if data_num > 30:
            break
        important_data_string += chat_data[0] + "\n"
    retrieve = generate_retrieve.run(query = focal_points, name = npc + "'s", event = important_data_string)

    previous = Database.get_all_documents(db, user, "Retrieves")
    print(previous)
    data_num = 0
    node = 0

    for i in previous:
        data_num += 1
    
    if data_num != 0:
        print(i)
        node = i["node"]
        node += 1
    
    datetimeStr = datetime.now().strftime("%Y-%m-%d")
    document_user = {"_id":ObjectId(),"node":node,"timestamp":datetimeStr,"retrieve":retrieve,"name":npc}
    print(Database.set_document(db, user, "Retrieves", document_user))