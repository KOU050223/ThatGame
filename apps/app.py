from flask import Flask, jsonify,request
from flask_socketio import SocketIO, send,emit
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # CORSを有効にする
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return jsonify({"message": "CCレモンゲームへようこそ！"})

@socketio.on('message')
def handleMessage(msg):
    print('Message: ' + msg)
    emit(msg, broadcast=True)

@app.route('/play', methods=['POST'])  # POSTメソッドを許可
def handle_post():
    data = request.json  # 受信したJSONデータを取得
    print(data)
    return jsonify({"message": "データを受け取りました"}), 200

if __name__ == '__main__':
    socketio.run(app, debug=True)