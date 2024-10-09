from flask import Flask, render_template, Blueprint, request, redirect, url_for,jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

CORS(app)  # これでFlask全体でCORSが有効になる
# グローバル変数として rooms を定義
rooms = {}

rooms_actions = {}  # 各ルームのプレイヤーのアクションを管理

# Blueprintの作成
samplesite = Blueprint(
    "app",
    __name__,
    template_folder="templates",
    static_folder="static"
)

# ロビーのルート
# @samplesite.route('/')
# def lobby():
#     # 満員でない部屋だけを取り出す
#     ava_rooms = {room: users for room, users in rooms.items() if len(users) < 2}
#     return render_template('lobby.html', rooms=ava_rooms)

# # ルーム作成のルート
# @samplesite.route('/create_room', methods=['POST'])
# def create_room():
#     room_name = request.form['room_name']
#     if room_name not in rooms:
#         rooms[room_name] = []
#     return redirect(url_for('sampleSite.join_room_view', room_name=room_name))

# # @samplesite.route('/create_room', methods=['POST'])

# # def create_room():
# #     room_name = request.json.get('room_name')
# #     if room_name not in rooms:
# #         rooms[room_name] = []
# #     return jsonify({'status': 'Room created', 'room_name': room_name})

# @app.route('/rooms', methods=['GET'])
# def get_rooms():
#     return jsonify(list(rooms.keys()))

# @socketio.on('create_room')
# def on_create_room(data):
#     room_name = data['room_name']
#     if room_name not in rooms:
#         rooms[room_name] = []
#         # 新しいルームが作成されたことをすべてのクライアントに通知
#         emit('room_list_update', {'room_name': room_name}, broadcast=True)

# # ルーム参加のルート
# @samplesite.route('/room/<room_name>')
# def join_room_view(room_name):
#     if room_name in rooms and len(rooms[room_name]) < 2:
#         return render_template('room.html', room_name=room_name)
#     else:
#         return redirect(url_for('sampleSite.lobby'))

# @socketio.on('join')
# def on_join(data):
#     room_name = data['room']
#     username = data['username']

#     if room_name in rooms and len(rooms[room_name]) < 2:
#         join_room(room_name)
#         rooms[room_name].append(username)
#         emit('status', {'msg': f'{username} has joined the room.'}, room=room_name)
#         emit('room_info', {'users': rooms[room_name]}, room=room_name)
#     else:
#         emit('status', {'msg': 'Room is full.'})

# @socketio.on('leave')
# def on_leave(data):
#     room_name = data['room']
#     username = data['username']

#     leave_room(room_name)
#     rooms[room_name].remove(username)
#     emit('status', {'msg': f'{username} has left the room.'}, room=room_name)

# -----------------------------------------------------------------

@socketio.on('message')
def handle_message(data):
    room_name = data['room']
    msg = data['msg']
    username = data['username']
    emit('message', {'msg': f'{username}:{msg}'})


@socketio.on('connect')
def test_connect():
    print('クライアントが接続しました')

@socketio.on('disconnect')
def test_disconnect():
    print('クライアントが切断されました')


@app.route('/play', methods=['POST'])  # POSTメソッドを許可
def handle_post():
    data = request.json  # 受信したJSONデータを取得
    print(data)
    return jsonify({"message": "データを受け取りました"}), 200

@app.route('/rooms')
def get_rooms():
    # 現在のルームリストをJSON形式で返す
    return jsonify(list(rooms.keys()))

@socketio.on('create_room')
def on_create_room(data):
    room_name = data['room_name']
    print(rooms)
    if room_name not in rooms:
        rooms[room_name] = []
        emit('room_list_update', {'room_name': room_name}, broadcast=True)

@socketio.on('join')
def on_join(data):
    room_name = data['room']
    username = data['username']

    if room_name in rooms and len(rooms[room_name]) < 2:
        join_room(room_name)
        rooms[room_name].append(username)
        emit('status', {'msg': f'{username} has joined the room.'})
        emit('room_info', {'users': rooms[room_name]})
    else:
        emit('status', {'msg': 'Room is full.'})










@socketio.on('player_action')
def handle_player_action(data):
    room_name = data['room']
    username = data['username']
    action = data['action']  # 'charge', 'attack', 'defense' など

    # ルームが存在しない場合、初期化
    if room_name not in rooms_actions:
        rooms_actions[room_name] = {}

    # プレイヤーのアクションを保存
    rooms_actions[room_name][username] = action
    print("データ",room_name,username,rooms_actions[room_name][username])
    # アクション確認メッセージを送信
    emit('action_confirmation', {'username': username, 'action': action})

    # 両プレイヤーがアクションを入力しているか確認
    if len(rooms_actions[room_name]) == 2:
        print("両者入力完了")
        # ここでアクションの結果を処理
        result = process_actions(rooms_actions[room_name])
        print(result)
        # 両プレイヤーに結果を送信
        emit('action_result', result, room=room_name)
        
        # アクションをクリア
        rooms_actions[room_name].clear()

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
        'player1': {'username': player1, 'action': action1},
        'player2': {'username': player2, 'action': action2},
        'winner': winner if winner != 'draw' else None,  # 引き分けの場合は None
        'is_draw': winner == 'draw'  # 引き分けかどうかを示すフラグ
    }
    
    return result


# Blueprintの登録
app.register_blueprint(samplesite)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=443)
