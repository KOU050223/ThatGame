from flask import Flask, render_template, Blueprint, request, redirect, url_for,jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

CORS(app)  # これでFlask全体でCORSが有効になる
# グローバル変数として rooms を定義
rooms = {}

# Blueprintの作成
sample_site = Blueprint(
    "sampleSite",
    __name__,
    template_folder="templates",
    static_folder="static"
)

# ロビーのルート
@sample_site.route('/')
def lobby():
    return render_template('lobby.html', rooms=rooms)

# ルーム作成のルート
# @sample_site.route('/create_room', methods=['POST'])
# def create_room():
#     room_name = request.form['room_name']
#     if room_name not in rooms:
#         rooms[room_name] = []
#     return redirect(url_for('sampleSite.join_room_view', room_name=room_name))

@sample_site.route('/create_room', methods=['POST'])
def create_room():
    room_name = request.json.get('room_name')
    if room_name not in rooms:
        rooms[room_name] = []
    return jsonify({'status': 'Room created', 'room_name': room_name})

@app.route('/rooms', methods=['GET'])
def get_rooms():
    return jsonify(list(rooms.keys()))

@socketio.on('create_room')
def on_create_room(data):
    room_name = data['room_name']
    if room_name not in rooms:
        rooms[room_name] = []
        # 新しいルームが作成されたことをすべてのクライアントに通知
        emit('room_list_update', {'room_name': room_name}, broadcast=True)
        
# ルーム参加のルート
@sample_site.route('/room/<room_name>')
def join_room_view(room_name):
    if room_name in rooms and len(rooms[room_name]) < 2:
        return render_template('room.html', room_name=room_name)
    else:
        return redirect(url_for('sampleSite.lobby'))

@socketio.on('join')
def on_join(data):
    room_name = data['room']
    username = data['username']

    if room_name in rooms and len(rooms[room_name]) < 2:
        join_room(room_name)
        rooms[room_name].append(username)
        emit('status', {'msg': f'{username} has joined the room.'}, room=room_name)
    else:
        emit('status', {'msg': 'Room is full.'})

@socketio.on('leave')
def on_leave(data):
    room_name = data['room']
    username = data['username']

    leave_room(room_name)
    rooms[room_name].remove(username)
    emit('status', {'msg': f'{username} has left the room.'}, room=room_name)

@socketio.on('message')
def handle_message(data):
    room_name = data['room']
    msg = data['msg']
    emit('message', {'msg': msg}, room=room_name)

# Blueprintの登録
app.register_blueprint(sample_site)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5003)
