import json
import requests

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

def count_tokens(messages):
    return sum([len(message["content"].split()) for message in messages])

def send_webhook(webhook_url, message):
    webhook_data = {
        "content": message
    }
    webhook_response = requests.post(webhook_url, data=webhook_data)

def send_admin_message(message):
    webhook_url = "https://discord.com/api/webhooks/1156485661617033258/7qIL5kp9mBYVVKz-_Scg-nBGi0NHb0Zi1RwXmfPValkp06rX7yvXmLbiweP4SkgSKb-b"
    send_webhook(webhook_url, message)

def send_character1_message(message):
    webhook_url = "https://discord.com/api/webhooks/1156466370016456704/TgcCSU_1JsMoR5A22q0Pah_FCFqX5_5k_Zsb7_F8i9hLOLlww0F5Z8W1WyJXqCABbBfA"
    send_webhook(webhook_url, message)

def send_character2_message(message):
    webhook_url = "https://discord.com/api/webhooks/1156466336009044018/BWeudD1_kyCwyGwbY4Hsv3l6ykBAx3KL9XpmCkr2PNv2IHxLXbWIGdPqiUZuK4sZZltW"
    send_webhook(webhook_url, message)

conversation = [
    "admin:::turn_garen",
    "1:::럭스, 오늘 훈련은 어떻게 됐어?",
    "admin:::turn_lux",
    "2:::괜찮았어. 마법을 좀 더 효율적으로 사용하는 방법을 연습했어. 그런데 오빠는? 다른 챔피언들과는 어떻게 됐어?",
    "admin:::turn_garen",
    "1:::조금 더 많은 훈련이 필요한 것 같아. 오늘은 훈련을 더 하고 싶은데, 너는 어때?",
    "admin:::join_user",
    "admin:::turn_garen",
    "1:::어? 너는... 여기 있는 새로운 얼굴이군. 넌 누구야?",
    "admin:::turn_user",
    "admin:::turn_lux",
    "2:::안녕하세요! 오늘 처음 보는 것 같네요.",
    "admin:::turn_user",
    "admin:::turn_garen",
    "1:::건희씨, 데마시아에 오신 것을 환영합니다! 여기서 어떤 일로 오셨나요?"
]
# 위와 같은 상황에서 유저가 난입해서 대화를 이어나갈거야. 가렌 또는 럭스가 먼저 유저가 난입했다는 것을 인지하고 대화를 이어나고자 해. 누가 먼저 어떻게 이야기하는 것이 자연스러울까?

def initiate():
    conversation_index = -1

    send_admin_message("Conversation started.")
    #send_character1_message("Conversation started.")
    
    while (True):
        print("input: ")
        user_input = str(input())
        if (user_input == "exit"):
            break
        else:
            conversation_index += 1
            transcript = conversation[conversation_index]
            turn = transcript.split(":::")[0]
            script = transcript.split(":::")[1]
            print(f"""
                -------
                index: {conversation_index}
                turn: {turn}
                script: {script}
                -------
            """)
            if (turn == "admin"):
                send_admin_message(script)
            elif (turn == "1"):
                send_character1_message(script)
            elif (turn == "2"):
                send_character2_message(script)

initiate()