from flask import Flask, render_template, Blueprint
from flask_socketio import SocketIO, emit

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

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5003)