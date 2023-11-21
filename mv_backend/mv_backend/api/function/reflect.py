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
from mv_backend.lib.database import Database
from mv_backend.lib.common import CommonChatOpenAI

OPENAI_API_KEY = "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"

openai.api_key = OPENAI_API_KEY
import os
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

MONGODB_CONNECTION_STRING = "mongodb+srv://geonhui:dotgeon@metaverse.px60xor.mongodb.net/?"

db = Database()

chat = CommonChatOpenAI()

embeddings_model = OpenAIEmbeddings()
# every prompts for this code

# generate the query score
# !<INPUT 0>! -- Event/thought statements 
# !<INPUT 1>! -- Count 
generate_query_template = """
{event}

Given only the information above, what are {num} most salient high-level questions we can answer about the subjects grounded in the statements?
1)
"""
generate_query_prompt = PromptTemplate(
    input_variables=["event", "num"], template=generate_query_template
)

generate_query = LLMChain(
    llm=chat,
    prompt=generate_query_prompt
)
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
generate_insights_template = """
Input:
{event}

Insights into conversational styles(e.g., Sociable), interests(e.g., soccer).
Insights:
    Information about *{opponent}*’s interests.
    Information about the topic *{opponent}* is curious about.
    The *{opponent}*'s conversation style (e.g., Sociable:  This child initiates interactions with others and is quick to respond to others initiations. Even if they only have few words or are hard to understand they continue to try and communicate with others. 
, Reluctant: This child is more likely to respond to others than to initiate an interaction on their own. This child may be labelled as “shy” and may need time to “warm up” to become comfortable with new people and new environments. This child’s communicative attempts might fly under the radar so try and lookout for them. Having difficulties with communication may decrease confidence and decrease attempts at interacting with others. 
, Passive: This child rarely responds and rarely initiates interactions with others. Children who have this communication style may be hard to connect with because they may seem uninterested in people and objects such as toys. A developmental delay, a sickness or being on medications may lead to this more passive communication style.
, Curious: Children with this style are naturally inquisitive and seek out interactions to satisfy their curiosity. They actively engage in conversations and activities that pique their interest, asking questions and exploring their surroundings. Their eagerness to learn and discover may drive them to initiate conversations or activities, often demonstrating a keen interest in various subjects or objects. They might not always wait for prompts and can be proactive in seeking new information or experiences. Their communication style is marked by a genuine thirst for knowledge and exploration.
, Aggressive: Children with this communication style tend to assert themselves forcefully in interactions. They might initiate communication or respond assertively, often dominating conversations or activities. Their expressions can be intense, sometimes coming off as confrontational or overly assertive. This behavior might stem from frustration, a desire for control, or an attempt to establish dominance. They might interrupt conversations, use strong language, or display physical aggression to communicate their needs or desires. This communication style may require guidance and support to channel their energy and assertiveness positively.
   Information about the topic of conversation between {name} and {opponent}.

What are the {name}'s high-level insights about {opponent} can be inferred from the above statement?
For interest, conversation style parts, you should refer to the sentences spoken by {opponent}.
example:
    interest: soccer, spacecraft, game
    conversation style: Passive
    topic of conversation: price of spacecraft
output format:
    interest: (noun)
    conversation style: (noun)
    topic of conversation: (noun)
"""
generate_insights_prompt = PromptTemplate(
    input_variables=["name", "opponent", "event"], template=generate_insights_template
)

generate_insights = LLMChain(
    llm=chat,
    prompt=generate_insights_prompt
)
def reflect(npc, user, chat_data_list):
    # openai_response = openai.ChatCompletion.create(
    #     model="gpt-3.5-turbo",
    #     messages=body["messages"]
    # )

    ### mongoDB user's memory ###
    # conversation = db.get_recent_documents(user, "Conversations")
    data_num = 0
    all_chat_data = []
    all_chat_data_node = []
    all_chat_data_string = ""
    for chat_data in reversed(chat_data_list):
        data_num += 1
        all_chat_data.append(chat_data)
        all_chat_data_node.append("[" + str(data_num) + "]" + chat_data)
        # all_chat_data.append(chat_data)
        all_chat_data_string += chat_data + "\n"
    
    if data_num == 0:
        return

    # conversation = Database.get_all_documents(db, user, "conversations")
    # data_num = 0
    # important_sum = 0
    # all_chat_data = []
    # before_chat_data = []
    # all_chat_data_node = []
    # important = []
    # for chat_data in conversation:
    #     if (chat_data["name"] == npc) or (chat_data["opponent"] == npc):
    #         data_num += 1
    #         before_chat_data.append(chat_data["name"] + ": " + chat_data["memory"])
    #         # important.append(int(chat_data["important"]))
    
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
    # all_chat_data_string = ""
    # for chat_data in reversed(before_chat_data):
    #     data_num += 1
    #     if data_num > 100:
    #         break
    #     all_chat_data_node.append("[" + str(data_num) + "]" + chat_data)
    #     all_chat_data.append(chat_data)
    #     all_chat_data_string += chat_data + "\n"

    # all_chat_data = []
    # all_chat_data_node = []
    # all_chat_data_string = ""
    # # now reflect with 100 message data (we wil generate only one query)
    # data_num = 0
    # for chat_data in reversed(body["messages"]):
    #     data_num += 1
    #     if data_num > 100:
    #         break
    #     all_chat_data_node.append("[" + str(data_num) + "]" + chat_data["role"] + ": " + chat_data["content"])
    #     all_chat_data.append(chat_data["role"] + ": " + chat_data["content"])
    #     all_chat_data_string += chat_data["role"] + ": " + chat_data["content"] + "\n"


    focal_points = generate_query.run(event = all_chat_data_string, num = "1")
    embedded_query = embeddings_model.embed_query(focal_points)
    embedings = embeddings_model.embed_documents(all_chat_data)

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
    important_data_string += generate_important.run(event = all_chat_data_string, name = user)
    data_num = 5
    for chat_data in sorted_dict:
        data_num += 1
        if data_num > 10:
            break
        important_data_string += chat_data[0] + "\n"
    insights = generate_insights.run(name = npc, opponent = user, event = important_data_string)

    previous = Database.get_all_documents(db, user, "Reflects")
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
    document_user = {"_id":ObjectId(),"node":node,"timestamp":datetimeStr,"reflect":insights,"name":npc}
    print(Database.set_document(db, user, "Reflects", document_user))

    return insights