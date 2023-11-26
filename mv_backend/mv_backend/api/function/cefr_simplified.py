from django.http import HttpResponse, JsonResponse
import requests
import json
from datetime import datetime
from bson.objectid import ObjectId

from mv_backend.lib.database import Database

def cefr(user, chat_data_list):
    url = "http://127.0.0.1:3000/analyze/cefr/"
    
    
    db = Database()

    data_num = 0
    all_chat_data_string = ""
    for chat_data in reversed(chat_data_list):
        data_num += 1
        if data_num > 30:
            break
        all_chat_data_string += chat_data + "\n"


    data = {
        "content": "{all_chat_data_string}"
    }
    
    response = requests.post(url, data=json.dumps(data), headers={'Content-Type': 'application/json'})
    response_json = response.json()
    
    cur_cefr = response_json["meta"]["grade"] #generate_cefr.run(CEFR = CEFR, name = user, query = all_chat_data_string)
    # cur_interest = generate_interest.run(query = all_chat_data_string)
    print(cur_cefr)
    cefr = Database.get_recent_documents(db, user, "CEFR", 1)
    
    cefr_string = "Idk"
    now_cefr = ""
    now_cefr = cur_cefr
    for i in cefr:
        cefr_string = i["cefr"]

    if cur_cefr == "IDK":
        cur_cefr = cefr_string
        now_cefr = "Idk"
    
    cefr_data = Database.get_all_documents(db, user, "CEFR")
    print(cefr_data)
    node = 0
    data_num = 0

    for i in cefr_data:
        data_num += 1
    
    if data_num != 0:
        node = i["node"] + 1
    
    datetimeStr = datetime.now().strftime("%Y-%m-%d")
    
    document_user = {"_id":ObjectId(),"node":node,"timestamp":datetimeStr,"cefr":cur_cefr}

    print(Database.set_document(db, user, "CEFR", document_user))

    return now_cefr