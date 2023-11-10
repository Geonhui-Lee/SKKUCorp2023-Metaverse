from langchain.chat_models import ChatOpenAI

gpt_model_name = 'gpt-4-1106-preview'

def CommonChatOpenAI():
    return ChatOpenAI(model_name=gpt_model_name, temperature=0)