from database import Database
from gitignore.env import OPENAI_API_KEY
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
from langchain.memory import ConversationBufferMemory
from datetime import datetime
from bson.objectid import ObjectId
import openai
chat = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0.1)

db = Database()

openai.api_key = OPENAI_API_KEY
import os
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

user_template = """""";
npc_template = """""";

user_prompt = PromptTemplate(
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

user_response = user_llm.run(input = "Hi")
all_chat = list()
all_importance = list()

for i in range(50):
  npc_response = npc_llm(input = user_response)
  print(npc_response)
  all_chat.append(f"{npc_response}")
  score = important_score.run(name = f"{user_name}", event = f"{npc_name}" + ": " + npc_response)
  all_importance.append(score)
  
  user_response = user_llm(input = npc_response)
  all_chat.append(f"{user_response}")
  print(user_response)
  score = important_score.run(name = f"{user_name}", event = f"{user_name}" + ": " + user_response)
  all_importance.append(score)

datetimeStr = datetime.now().strftime("%Y-%m-%d")

for i in range(len(all_chat)):
  document_user = {"_id":ObjectId(),"node":i,"timestamp":datetimeStr,"memory":all_chat[i],"name":f"{npc_name}","opponent":f"{user_name}","important":all_importance[i]}

  document_customer = {"_id":ObjectId(),"node":i+1,"timestamp":datetimeStr,"memory":all_chat[i+1],"name":f"{user_name}","opponent":f"{npc_name}","important":all_importance[i]}
  
  i+=2
  print(Database.set_document(db, "conversations", "f{user_name}", document_user))
  print(Database.set_document(db, "conversations", "f{user_name}", document_customer))
  
  

  