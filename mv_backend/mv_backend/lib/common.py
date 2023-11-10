from langchain.chat_models import ChatOpenAI

def CommonChatOpenAI():
    return ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)