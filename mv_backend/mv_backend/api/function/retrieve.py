import openai
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import numpy as np
from numpy.linalg import norm
from langchain.embeddings import OpenAIEmbeddings
from datetime import datetime
from bson.objectid import ObjectId
from mv_backend.lib.database import Database
from mv_backend.lib.common import CommonChatOpenAI
from mv_backend.settings import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY
import os
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

db = Database()

chat = CommonChatOpenAI()

embeddings_model = OpenAIEmbeddings()

# every prompts for this code

# prompt: find 5 important conversations
#
# input:
# {event} -- converstation converstation (user <-> npc)
# {name} -- user's name
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

# prompt: Create NPC answer to a query about the user
# 
# input:
# {query} -- final_points (provides specific criteria)
# {name} -- npc's name
# {opponent} -- user's name
# {event} -- converstation converstation (user <-> npc)
# 
# what the user is bad at: grammar, impolite or morally wrong
generate_template = """
Query:
Find out what the *{opponent}* is bad at (grammar, impolite or morally wrong, etc.)
(user is only *{opponent}*.)
{query}
Input:
{event}

What the *answer* to the query can {name} infer from the above statements?
If content is None, *do not* show content. If there is no content, only show "None". Don't show duplicate data.
example:
grammar mistake: 1. <color=red>"How much airship?"</color> -> <color=green>"How much does an airship cost?"</color>\nreason: Interrogative Grammar
vocabulary mistake: None
bad manners: 1. <color=red>"Shut up."</color>\nreason: rude and disrespectful
output format:
grammar mistake: 1. <color=red></color> -> <color=green></color>\nreason: (noun)\n2. ...
vocabulary mistake: 1. <color=red></color> -> <color=green></color>\nreason: (noun)\n2. ...
bad manners: 1. <color=red>(conversation content)</color>\nreason: (noun)\n2. ...
"""
generate_prompt = PromptTemplate(
    input_variables=["query", "name", "opponent", "event"], template=generate_template
)

generate_retrieve = LLMChain(
    llm=chat,
    prompt=generate_prompt
)

# retrieve:
# -- Retrieve Phase --
#   Find 15 conversations using 3 criteria
#   3 criteria:
#   relevance -- relevance to retrieve query (embedding and cosine similarity)
#   recency -- conversation recency score (For previous conversations, start at 1 and multiply by 0.995)
#   importance -- find important conversations
#
# -- Generate Phase --
#   Generate NPC answer to a query about the user
#
# input:
# npc -- npc's name
# user -- user's name
# chat_data_list -- conversation
def retrieve(npc, user, chat_data_list):
    data_num = 0                        # the number of data
    all_chat_data = []                  # One session conversation (list)
    all_chat_data_node = []             # One session conversation with node (list)
    all_chat_data_string = ""           # One session conversation (string)
    retrieve = ""                       # npc's answer (what the user is bad at)

    # Organize One session conversations
    for chat_data in reversed(chat_data_list):
        data_num += 1
        all_chat_data.append(chat_data)
        all_chat_data_node.append("[" + str(data_num) + "]" + chat_data)
        all_chat_data_string += chat_data + "\n"
    
    # If the number of data is 0, return empty retrieve
    if data_num == 0:
        return retrieve
    
    # retrieve query (High-level question that NPC might think about during conversation)
    focal_points = "Find out what the user is bad at (grammar, understanding of context, etc.)"
    
    # final_points prompt (provides specific criteria)
    final_points = """
    If the user has made a gramatical mistake conduct the following tasks.
    1. find and explain the gramatical mistakes the user has made with the specific grammar. (Except punctuation and capitalization)
    2. *Always* show the *exact* sentence the user made a mistake in.
    3. Correct sentences that the user made a mistake and show them.

    If the user has made a bad manners conduct the following tasks.
    1. find and explain the bad manners the user has made.
    2. *Always* show the *exact* sentence the user made the bad manners.
    """

    # -- Retrieve Phase --
    # query embedding (LangChain - Text embedding models - embed query)
    embedded_query = embeddings_model.embed_query(focal_points)
    # conversation embedding (LangChain - Text embedding models - embed documents)
    embeddings = embeddings_model.embed_documents(all_chat_data_string)

    # relevance score: cosine similarity between two embeddings
    cosine = np.dot(embeddings, embedded_query)/(norm(embeddings, axis=1)*norm(embedded_query))

    # Binding conversation and relevance score
    chat_data_score = dict(zip(all_chat_data_node, cosine))

    data_num = 0
    recency = 1                         # recency score

    # Calculate recency score and add it to the relevance score.
    for chat_data in all_chat_data:
        data_num += 1
        if data_num > 100:
            break
        recency *= 0.995

        chat_data_score["[" + str(data_num) + "]" + chat_data] += recency
    
    sorted_dict = sorted(chat_data_score.items(), key = lambda item: item[1], reverse = True)

    # Find 5 important conversations
    important_data_string = "[1] "
    important_data_string += generate_important.run(name = user, event = all_chat_data_string)

    # Find 10 conversations with the highest scores (relevance score + recency score)
    data_num = 5
    for chat_data in sorted_dict:
        data_num += 1
        if data_num > 15:
            break
        important_data_string += chat_data[0] + "\n"
    
    # -- Generate Phase --
    # Generate NPC insights about the user
    retrieve = generate_retrieve.run(query = final_points, name = npc + "'s", opponent = user, event = important_data_string)

    previous = Database.get_all_documents(db, user, "Retrieves")
    data_num = 0
    node = 0                            # data node

    for i in previous:
        data_num += 1
    
    # Find the next node
    if data_num != 0:
        print(i)
        node = i["node"]
        node += 1
    
    # timestamp
    datetimeStr = datetime.now().strftime("%Y-%m-%d")
    # Save NPC insights to database
    document_user = {"_id":ObjectId(),"node":node,"timestamp":datetimeStr,"retrieve":retrieve,"name":npc}
    print(Database.set_document(db, user, "Retrieves", document_user))

    return retrieve