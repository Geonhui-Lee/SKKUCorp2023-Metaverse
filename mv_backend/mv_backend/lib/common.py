from langchain.chat_models import ChatOpenAI
from mv_backend.settings import OPENAI_API_KEY
import openai

openai.api_key = OPENAI_API_KEY
gpt_model_name = 'gpt-4-1106-preview'
def CommonChatOpenAI():
    return ChatOpenAI(model_name=gpt_model_name, temperature=0)