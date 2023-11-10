from langchain.chat_models import ChatOpenAI

def CommonChatOpenAI():
    return ChatOpenAI(model_name='gpt-4-1106-preview', temperature=0)