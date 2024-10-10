from flask import Flask, render_template, Blueprint, request, redirect, url_for, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)  # Flask全体でCORSを有効化

# グローバル変数として rooms と roomsActions を定義
rooms = {}
roomsActions = {}  # 各ルームのプレイヤーのアクションを管理

# Blueprintの作成
sampleSite = Blueprint(
    "sampleSite",
    __name__,
    template_folder="templates",
    static_folder="static"
)

@socketio.on('connect')
def connect(data):
    print("接続した")

@socketio.on('disconnect')
def disconnect(data):
    print("切断されました")

@app.route('/rooms', methods=['GET'])
def get_rooms():
    # 現在のルームリストをJSON形式で返す
    return jsonify(list(rooms.keys()))

@socketio.on('create_room')
def on_create_room(data):
    roomName = data['roomName']
    print(f"Room created: {roomName}")  # ここでルーム名を確認
    if roomName not in rooms:
        rooms[roomName] = []
        emit('room_list_update', {'roomName': roomName}, broadcast=True)
        print(f"Emitted room_list_update for room: {roomName}")

@socketio.on('join')
def on_join(data):
    print("roomに入った")
    roomName = data['roomName']
    userName = data['userName']

    if roomName in rooms and len(rooms[roomName]) < 2:
        join_room(roomName)
        rooms[roomName].append(userName)
        emit('status', {'msg': f'{userName} has joined the room.'}, room=roomName)
        emit('room_info', {'users': rooms[roomName]}, room=roomName)
    else:
        emit('status', {'msg': 'Room is full.'})

@socketio.on('leave')
def on_leave(data):
    print("roomから出た")
    roomName = data['roomName']
    userName = data['userName']

    leave_room(roomName)
    rooms[roomName].remove(userName)
    emit('status', {'msg': f'{userName} has left the room.'}, room=roomName)

@socketio.on('message')
def handle_message(data):
    print("message来た")
    print(data)
    roomName = data['roomName']
    msg = data['msg']
    userName = data['userName']
    print(roomName,msg,userName)
    emit('message', {'msg': f'{userName}:{msg}'}, room=roomName)

@socketio.on('player_action')
def handle_player_action(data):
    roomName = data['roomName']
    userName = data['userName']
    action = data['action']  # 'charge', 'attack', 'defense' など

    # ルームが存在しない場合、初期化
    if roomName not in roomsActions:
        roomsActions[roomName] = {}

    # プレイヤーのアクションを保存
    roomsActions[roomName][userName] = action
    emit('action_confirmation', {'userName': userName, 'action': action})

    # 両プレイヤーがアクションを入力しているか確認
    if len(roomsActions[roomName]) == 2:
        result = process_actions(roomsActions[roomName])
        emit('action_result', result, room=roomName)
        # アクションをクリア
        roomsActions[roomName].clear()

def process_actions(actions):
    # 各プレイヤーのアクションに基づいて結果を計算するロジック
    player1, player2 = list(actions.keys())
    action1 = actions[player1]
    action2 = actions[player2]

    # 勝敗判定のロジック
    if action1 == action2:
        winner = 'draw'  # 両者が同じアクションを選択した場合は引き分け
    elif action1 == 'attack' and action2 == 'charge':
        winner = player1  # 攻撃がチャージに勝つ
    elif action1 == 'charge' and action2 == 'attack':
        winner = player2  # 攻撃がチャージに勝つ
    elif action1 == 'charge' and action2 == 'defense':
        winner = player1  # チャージが防御に勝つ
    elif action1 == 'defense' and action2 == 'charge':
        winner = player2  # チャージが防御に勝つ
    elif action1 == 'attack' and action2 == 'defense':
        winner = player1  # 攻撃が防御に勝つ
    elif action1 == 'defense' and action2 == 'attack':
        winner = player2  # 攻撃が防御に勝つ
    else:
        winner = 'draw'  # その他のケースでは引き分け

    # 結果を辞書で返す
    result = {
        'player1': {'userName': player1, 'action': action1},
        'player2': {'userName': player2, 'action': action2},
        'winner': winner if winner != 'draw' else None,  # 引き分けの場合は None
        'isDraw': winner == 'draw'  # 引き分けかどうかを示すフラグ
    }
    return result

# Blueprintの登録
app.register_blueprint(sampleSite)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=443)
