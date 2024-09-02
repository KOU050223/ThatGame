from flask import Blueprint,render_template
from apps.sampleSite.forms import KweetForm
from apps.sampleSite.models import Kweet
from apps.app import db
import requests
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

sampleSite = Blueprint(
    "sampleSite",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="static/sampleSite"
)

# API通信に必要なヘッダ情報
headers ={
    "Authorization":OPENAI_API_KEY,
    "Content-Type":"application/json"
}

# POSTしてきた値を保持するためのリスト情報
messageList = []

@sampleSite.route('/',methods=["GET","POST"]) #http://○○/で実行
def index():
    global messageList
    form = KweetForm()
    if form.is_submitted():
        print("submit!")
        # いったん変数にmessageの内容を入れる
        message = form.message.data or ''
        if message != '':
            # API通信用のbodyを作成
            body = {
                "model":"gpt-4o-mini",
                "messages":[
                    {
                    "role":"user",
                    "content":message
                    }
                ]
            }
            # API通信
            response = requests.post("https://api.openai.com/v1/chat/completions",headers=headers,json=body)
            # レスポンス内容をprintする
            print(response.status_code)
            print(response.json())
            # データベースに登録&レスポンスも
            kweet = [Kweet(message=message),
                     Kweet(message=response.json()['choices'][0]['message']['content'])         
            ]
            # db.session.add(kweet)
            db.session.bulk_save_objects(kweet)
            db.session.commit()
            # リストに値を追加
            # messageList.append(message)
            messageList=Kweet.query.all()
            # 取得したリストを反転（下のリストを変えてしまう）
            messageList.reverse()
    
    dbData ={
        "id":123,
        "name":"KOU",
        "form":form,
        "messageList":messageList,
        "len":len(messageList)
    }
    return render_template("index.html",data = dbData)
