from mv_backend.lib.database import Database
from mv_backend.settings import OPENAI_API_KEY
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from datetime import datetime
from bson.objectid import ObjectId
import openai
chat = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0.1)

db = Database()

openai.api_key = OPENAI_API_KEY
import os
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

user_template = """
You are a 6 year old student that has a lot of curiosity you like to question about everything. *Always* make the response in a way that a 6 year old child would answer.
If the user input seems to be too hard for a 6 year old child to answer, respond like you don't know the answer.

CEFR is the English's level criteria established by the Common European Framework of Reference for Languages, which ranges from A1 to C2 (pre-A1,A1,A2,B1,B2,C1,C2).
Please talk according to the user's English level. The user's English level is provided as a CEFR indicator and the customer's CEFR is {user_cefr}.

Opponent:{npc_input}
User:"""
npc_template = """"""
user_name = "user0"
npc_name = "pizza chef"
user_cefr = "pre-A1"

user_prompt = PromptTemplate(
    input_variables= ["user_cefr", "user_input"],
    template=user_template
)

npc_prompt = PromptTemplate(
    template=user_template
)

user_llm = LLMChain(
    llm=chat,
    prompt=user_prompt,
    memory = ConversationBufferMemory()
)

npc_llm = LLMChain(
    llm=chat,
    prompt=npc_prompt,
    memory = ConversationBufferMemory()
)

important_template = """
On the scale of 1 to 10, where 1 is purely mundane (e.g., routine morning greetings) and 10 is extremely poignant (e.g., a conversation about breaking up, a fight), rate the likely poignancy of the following conversation for {name}.

Conversation: 
{event}

Rate (return a number between 1 to 10):
"""
important_prompt = PromptTemplate(
    input_variables=["name", "event"], template=important_template
)

important_score = LLMChain(
    llm=chat,
    prompt=important_prompt
)

print(f"{npc_name}: Hi I'm {npc_name}.")
user_response = user_llm.run(user_cefr = user_cefr, npc_input = f"Hi I'm {npc_name}.")
print(f"{user_name}: {user_response}")
all_chat = list()
all_importance = list()

for i in range(50):
  npc_response = npc_llm()
  print(f"{npc_name}: {npc_response}")
  all_chat.append(f"{npc_response}")
  score = important_score.run(name = f"{user_name}", event = f"{npc_name}" + ": " + npc_response)
  all_importance.append(score)
  
  user_response = user_llm(user_cefr = user_cefr, npc_input = npc_response)
  all_chat.append(f"{user_response}")
  print(f"{user_name}: {user_response}")
  score = important_score.run(name = f"{user_name}", event = f"{user_name}" + ": " + user_response)
  all_importance.append(score)

datetimeStr = datetime.now().strftime("%Y-%m-%d")

for i in range(len(all_chat)):
  document_user = {"_id":ObjectId(),"node":i,"timestamp":datetimeStr,"memory":all_chat[i],"name":f"{npc_name}","opponent":f"{user_name}","important":all_importance[i]}

  document_customer = {"_id":ObjectId(),"node":i+1,"timestamp":datetimeStr,"memory":all_chat[i+1],"name":f"{user_name}","opponent":f"{npc_name}","important":all_importance[i]}
  
  i+=2
  print(Database.set_document(db, "conversations", "f{user_name}", document_user))
  print(Database.set_document(db, "conversations", "f{user_name}", document_customer))
  
  

  