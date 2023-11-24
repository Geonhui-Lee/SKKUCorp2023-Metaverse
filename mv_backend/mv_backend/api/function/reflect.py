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
###
origin_insights_template = """
    Statements about {opponent}
    {event}
    What 5 high-level insights can {name} infer from
    the above statements? (example format: insight
    (because of 1, 5, 3))
"""
origin_insights_prompt = PromptTemplate(
    input_variables=["name", "opponent", "event"], template=origin_insights_template
)

origin_insights = LLMChain(
    llm=chat,
    prompt=origin_insights_prompt
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
    The *{opponent}*'s conversation style (e.g., Extroverted: This child actively seeks out interactions with others and eagerly responds to others' initiatives. They thrive in social settings and are comfortable engaging with different people. Even with limited words or when facing communication challenges, they persist in their efforts to connect with others. Their enthusiasm for social engagement often leads them to initiate conversations and activities, displaying a natural ease in interacting with those around them.
, Introverted: In contrast, this child tends to respond more than initiate interactions. They may be labeled as "shy" and typically require time to feel comfortable in new environments or around new people. Their attempts at communication might go unnoticed as they prefer observing before participating actively. Difficulties in communication can affect their confidence, making them less likely to initiate interactions. However, they can be deeply engaged and thoughtful conversationalists once they feel at ease.
, Imaginative: This child actively engages in interactions, displaying a vibrant imagination in their conversations and activities. They initiate interactions and respond enthusiastically, infusing creativity into their communication. Their imaginative nature leads them to enjoy storytelling, creative play, and exploring various possibilities in their interactions. They often bring a sense of wonder and creativity to their social engagements, making interactions dynamic and imaginative.
, Intuitive: In contrast, this child might not always initiate interactions but demonstrates a deep intuitive understanding of their surroundings and people. While they may be more reserved in social situations, they possess a remarkable ability to perceive emotions and nuances. When they do engage, their interactions are marked by thoughtfulness and insight, showcasing their intuitive understanding of others' feelings and the environment.
, Curious: Children with this style are naturally inquisitive and seek out interactions to satisfy their curiosity. They actively engage in conversations and activities that pique their interest, asking questions and exploring their surroundings. Their eagerness to learn and discover may drive them to initiate conversations or activities, often demonstrating a keen interest in various subjects or objects. They might not always wait for prompts and can be proactive in seeking new information or experiences. Their communication style is marked by a genuine thirst for knowledge and exploration.
, Aggressive: Children with this communication style tend to assert themselves forcefully in interactions. They might initiate communication or respond assertively, often dominating conversations or activities. Their expressions can be intense, sometimes coming off as confrontational or overly assertive. This behavior might stem from frustration, a desire for control, or an attempt to establish dominance. They might interrupt conversations, use strong language, or display physical aggression to communicate their needs or desires. This communication style may require guidance and support to channel their energy and assertiveness positively.
, Polite: This child demonstrates a respectful and considerate approach in their interactions with others. They are attentive to social norms, use courteous language, and show good manners. They tend to wait for their turn to speak, listen actively, and respond thoughtfully. Their communication style reflects a genuine effort to be kind and considerate to others, often using phrases like "please" and "thank you" and showing empathy in their interactions.
, Impolite: In contrast, this child's communication style may come across as rude or lacking in social niceties. They might interrupt conversations frequently, ignore social cues, or use language that is considered disrespectful. Their interactions might seem abrupt or dismissive, showing less regard for others' feelings or social expectations. This behavior might stem from a lack of awareness rather than intentional rudeness, requiring guidance and coaching to understand and employ more appropriate communication manners.
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
# 외향적: 사교성을 좋아하고, 사람들과 쉽게 연결되며, 열심히 대화를 시작합니다.

# 내향적: 시작보다 응답하기를 선호하고, 참여하기 전에 편안함을 느끼고, 관찰하는 데 시간이 걸립니다.

# 상상력: 상호 작용에서 창의적이고, 스토리텔링과 창의적인 놀이를 즐기며, 대화에 창의력을 가져다 줍니다.

# 직관적: 감정과 뉘앙스를 지각하고, 사회적 환경에서 유보적이며, 참여할 때 사려 깊고 통찰력이 있습니다.

# 호기심: 호기심이 많고 적극적이며, 새로운 지식과 경험을 찾고, 배우고 탐색하기를 열망합니다.

# 공격적: 적극적인 상호작용, 강렬한 표현, 요구를 전달하기 위해 공격성을 사용할 수 있습니다.

# 예의: 존중하고 배려하며, 사회 규범에 주의하고, 정중한 언어를 사용하며, 상호 작용에 공감합니다.

# 무례한 행동: 무례하게 보이고, 사회적 신호를 무시하고, 예의가 없으며, 사회적 상호작용에서 지도가 필요할 수 있습니다.
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

    origin_insight = origin_insights.run(name = npc, opponent = user, event = important_data_string)
    document_user = {"_id":ObjectId(),"timestamp":datetimeStr,"reflect":origin_insight,"name":npc}
    print(Database.set_document(db, user, "Reflects_Origin", document_user))

    return insights