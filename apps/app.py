from flask import Flask, render_template, Blueprint,jsonify,request
from flask_socketio import SocketIO, emit
from flask_cors import CORS

# Flaskアプリケーションインスタンスの作成
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Blueprintの作成
sample_site = Blueprint(
    "sampleSite",
    __name__,
    template_folder="templates",
    static_folder="static"
)

@sample_site.route('/')
def index():
    return render_template('index.html')

@socketio.on('message')
def handle_message(data):
    emit('message', data, broadcast=True)

socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)  # CORSを有効にする

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
    socketio.run(app, host='0.0.0.0', port=5003,debug=True)
