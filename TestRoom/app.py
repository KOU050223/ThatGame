from flask import Flask, render_template, Blueprint, request, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# グローバル変数として rooms を定義
rooms = {}

# Blueprintの作成
samplesite = Blueprint(
    "sampleSite",
    __name__,
    template_folder="templates",
    static_folder="static"
)

# ロビーのルート
@samplesite.route('/')
def lobby():
    # 満員でない部屋だけを取り出す
    ava_rooms = {room: users for room, users in rooms.items() if len(users) < 2}
    return render_template('lobby.html', rooms=ava_rooms)

# ルーム作成のルート
@samplesite.route('/create_room', methods=['POST'])
def create_room():
    room_name = request.form['room_name']
    if room_name not in rooms:
        rooms[room_name] = []
    return redirect(url_for('sampleSite.join_room_view', room_name=room_name))

# ルーム参加のルート
@samplesite.route('/room/<room_name>')
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
        emit('room_info', {'users': rooms[room_name]}, room=room_name)
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
    username = data['username']
    emit('message', {'msg': f'{username}:{msg}'}, room=room_name)

# Blueprintの登録
app.register_blueprint(samplesite)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5003)