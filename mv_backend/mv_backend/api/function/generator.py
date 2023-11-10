from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from datetime import datetime
from bson.objectid import ObjectId
import openai

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from retrieve_auto_test import *
from reflect_auto_test import *

MONGODB_CONNECTION_STRING = "mongodb+srv://skku:skku@metaverse.px60xor.mongodb.net/?retryWrites=true&w=majority"
class Database:
    def __init__(self):
        self.client = MongoClient(MONGODB_CONNECTION_STRING, server_api=ServerApi('1'))
    
    def get_client(self):
        return self.client

    def get_database(self, database_name):
        return self.client[database_name]

    def get_collection(self, database_name, collection_name):
        return self.get_database(database_name)[collection_name]
    
    def get_all_collections(self, database_name):
        return self.get_database(database_name).list_collection_names()
    
    def get_all_documents(self, database_name, collection_name):
        return self.get_collection(database_name, collection_name).find()
    
    def set_document(self, database_name, collection_name, document):
        return self.get_collection(database_name, collection_name).insert_one(document)
    
    def set_documents(self, database_name, collection_name, documents):
        return self.get_collection(database_name, collection_name).insert_many(documents)

db = Database()
OPENAI_API_KEY = "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"
import os
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
chat = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=1)


user_template = """
You are a 6 year old student that has a lot of curiosity. You like to question everything. *Always* make the response in a way that a 6-year-old child would answer.
English level of 6-year-old child:
 1. Basic Vocabulary: Has a basic vocabulary consisting of common words and simple phrases. This might include everyday objects, colors, numbers, greetings, and some basic verbs and nouns.
 2. Grammar and Sentence Structure: Forms simple sentences. May use present tense verbs and basic sentence structures, but more complex grammar rules (e.g., past tense, conditional sentences) are less likely to be mastered.
 3. Communication Skills: Can communicate basic needs and wants. May be able to ask and answer simple questions, but more complex communication is difficult.
If the opponent's answer seems to be too hard for a 6 year old child to answer, respond like you don't know the answer.


CEFR is the English's level criteria established by the Common European Framework of Reference for Languages, which ranges from A1 to C2 (pre-A1,A1,A2,B1,B2,C1,C2).
Please talk according to the given English level. Your English level is provided as a CEFR indicator and your CEFR is {user_cefr}.


Your Opponent Job: {npc_name}
*Focus on questions about {npc_name}*

Memory: {history}
Opponent:{npc_input}
User:"""

npc_template = """
You're job is a Police Officer(do not forget).  *Always* Answer to the user briefly and concisely in a way that a Police Officer would answer.
situation : you are explaining to the user all about your job. *You are not in a ordering situation*.

CEFR is the English's level criteria established by the Common European Framework of Reference for Languages, which ranges from A1 to C2 (pre-A1,A1,A2,B1,B2,C1,C2).
Please talk to the user according to the user's English level. The user's English level is provided as a CEFR indicator and the user's CEFR is {user_cefr}.

Memory: {history}
Opponent:{user_input}
You:"""

user_name = "user0"
npc_name = "Police Officer"
user_cefr = "pre-A1"

user_prompt = PromptTemplate(
    input_variables= ["user_cefr", "npc_name", "npc_input", "history"],
    template=user_template
)

npc_prompt = PromptTemplate(
    input_variables= ["user_cefr","user_input", "history"],
    template=npc_template
)

user_llm = LLMChain(
    llm=chat,
    prompt=user_prompt
)

npc_llm = LLMChain(
    llm=chat,
    prompt=npc_prompt
)

# important_template = """
# On the scale of 1 to 10, where 1 is purely mundane (e.g., routine morning greetings) and 10 is extremely poignant (e.g., a conversation about breaking up, a fight), rate the likely poignancy of the following conversation for {name}.

# Conversation: 
# {event}

# Rate (return a number between 1 to 10):
# """
# important_prompt = PromptTemplate(
#     input_variables=["name", "event"], template=important_template
# )

# important_score = LLMChain(
#     llm=chat,
#     prompt=important_prompt
# )

print(f"{npc_name}: Hi I'm {npc_name}.")
user_response = input("")
print(f"{user_name}: {user_response}")
all_chat = list()
all_chat_string = ""
all_chat.append(f"{user_response}")
all_chat_string += f"{user_name}: {user_response}\n"
all_importance = list()

# score = important_score.run(name = f"{user_name}", event = f"{npc_name}" + ": " + user_response)
# score = "0" + score
# score_user = int(''.join(filter(str.isdigit, score)))
# if score_user == 110:
#     score_user = 0
# all_importance.append(score_user)

for i in range(15):
    npc_response = npc_llm.run(user_cefr = user_cefr, user_input = user_response, history = all_chat_string)
    print(f"{npc_name}: {npc_response}")
    all_chat.append(f"{npc_response}")
    all_chat_string += f"{npc_name}: {npc_response}\n"
    
    # score = important_score.run(name = f"{user_name}", event = f"{npc_name}" + ": " + npc_response)
    # score = "0" + score
    # score_user = int(''.join(filter(str.isdigit, score)))
    # if score_user == 110:
    #     score_user = 0
    # all_importance.append(score_user)
    
    user_response = input("")
    all_chat.append(f"{user_response}")
    all_chat_string += f"{user_name}: {user_response}\n"
    print(f"{user_name}: {user_response}")
    
    # score = important_score.run(name = f"{user_name}", event = f"{npc_name}" + ": " + user_response)
    # score = "0" + score
    # score_user = int(''.join(filter(str.isdigit, score)))
    # if score_user == 110:
    #     score_user = 0
    # all_importance.append(score_user)

datetimeStr = datetime.now().strftime("%Y-%m-%d")

i = 0
chat_length = len(all_chat)
while(i < chat_length):
  document_user = {"_id":ObjectId(),"node":i,"timestamp":datetimeStr,"memory":all_chat[i],"name":f"{user_name}","opponent":f"{npc_name}"}
  i += 1
  print(Database.set_document(db, f"{user_name}", "conversations",  document_user))
  
  if(i >= chat_length):
      break
  
  document_npc = {"_id":ObjectId(),"node":i,"timestamp":datetimeStr,"memory":all_chat[i],"name":f"{npc_name}","opponent":f"{user_name}"}
  i += 1
  
  print(Database.set_document(db, f"{user_name}", "conversations",  document_npc))


retrieve(f"{npc_name}", f"{user_name}")
reflect(f"{npc_name}", f"{user_name}")
  
  

  