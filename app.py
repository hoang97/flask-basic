import bot, time
from functools import wraps

from flask import Flask, render_template, request, send_from_directory, redirect, flash, make_response
from flask.helpers import url_for
from flask_socketio import Namespace, emit, SocketIO, join_room, leave_room, send

from models import User
import config

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
socketio = SocketIO(app)
IMAGES_ROOT = config.IMAGES_ROOT
MESSAGE_DB_DIR = config.MESSAGE_DB_DIR


# --------------------- Các functions----------------------------------

def save_to_database(username, room_name, message, timestamp):
    '''Lưu tin nhắn vào database'''
    with open(MESSAGE_DB_DIR,'a') as f:
        f.write(username + ';' + message + ';' + room_name + ';'+ timestamp +'\n')
        f.close()

def is_authenticated(request):
    '''Kiểm tra username, token trong database'''
    username = request.cookies.get('username', '')
    token = request.cookies.get('token', '')
    if token:
        try:
            user = User.filter(username=username)[0]
            return user.token == token
        except:
            pass
    return False

def login_required(func):
    @wraps(func)
    def vertify(*args, **kwargs):
        if is_authenticated(request):
            return func(*args, **kwargs)
        else:
            flash('Please login first!!!','error')
            return redirect(url_for('login'))
    return vertify

# --------------------------Xử lí Websocket--------------------------------

class ChatNameSpace(Namespace):

    def on_connect(self):
        username = request.args.get('username', '')
        room_name = request.args.get('room_name', '')
        join_room(room_name)
        print('User connected')
        
        # read data from database
        with open(MESSAGE_DB_DIR,'r') as f:
            while True:
                line = f.readline().strip()
                if not line:
                    break
                user, msg, room, timestamp = line.split(';')
                if room == room_name:
                    emit('server_message', {
                        'username':user, 
                        'message': msg,
                        'timestamp': timestamp,
                    })
            f.close()

        # send greeting smg
        bot_msg = bot.greeting(username, room_name)
        emit('server_message', bot_msg, to=room_name)
        save_to_database(bot_msg['username'], room_name, bot_msg['message'], bot_msg['timestamp'])
    
    def on_disconnect(self):
        username = request.args.get('username', '')
        room_name = request.args.get('room_name', '')
        leave_room(room_name)
        print('User disconnected')

        # send good bye msg
        bot_msg = bot.good_bye(username, room_name)
        emit('server_message', bot_msg, to=room_name)
        save_to_database(bot_msg['username'], room_name, bot_msg['message'], bot_msg['timestamp'])

    def on_client_message(self, data):
        username = request.args.get('username', '')
        room_name = request.args.get('room_name', '')
        message = data.get('message', '')
        timestamp = data.get('timestamp', '')

        save_to_database(username, room_name, message, timestamp)
        emit('server_message', {'username':username, 'message': message}, to=room_name)

        # send answer msg
        bot_msg = bot.answer(username, room_name, message)
        if bot_msg['message']:
            emit('server_message', bot_msg, to=room_name)
            save_to_database(bot_msg['username'], room_name, bot_msg['message'], bot_msg['timestamp'])

socketio.on_namespace(ChatNameSpace('/chat/'))

# ----------------------------Các Routes------------------------------------

@app.route('/chat/', methods=['GET'])
@login_required
def chat():
    username = request.cookies.get('username', '')
    room_name = request.args.get('room_name','')
    method = request.args.get('method','')

    return render_template('chat.html', username=username, room_name=room_name, method=method)

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    username = request.cookies.get('username', '')
    if request.method == 'POST':
        room_name = request.form.get('room_name', '')
        method = request.form.get('method', '')
        return redirect(url_for('chat', username=username, room_name=room_name, method=method))

    return render_template('index.html')

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if is_authenticated(request):
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        user_query = User.filter(username=username)
        if user_query:
            user = user_query[0]
            if user.authenticate(password):
                session_token = user.init_session()
                response = make_response(redirect(url_for('index')))
                response.set_cookie(key='username',value=username)
                response.set_cookie(key='token',value=session_token)
                flash('Đăng nhập thành công!','message')
                return response
            else:
                flash('Tên tài khoản hoặc mật khẩu không đúng', 'error')
        else:
            flash('Tên tài khoản hoặc mật khẩu không đúng!', 'error')

    return render_template('login.html')

@app.route('/logout/')
@login_required
def logout():
    username = request.cookies.get('username', '')
    User.filter(username=username)[0].terminate_session()
    flash('Đăng xuất thành công!', 'message')
    return redirect(url_for('login'))

@app.route('/register/', methods=['GET', 'POST'])
def register():
    if is_authenticated(request):
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')
        if password != password_confirm:
            flash('Mật khẩu không khớp!', 'error')
        elif User.filter(username=username):
            flash('Tài khoản đã tồn tại!', 'error')
        else:
            User.create(username, password)
            flash('Tạo tài khoản thành công', 'message')
            return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/edit-pwd/', methods=['GET', 'POST'])
@login_required
def edit_password():
    if request.method == 'POST':
        username = request.cookies.get('username')
        password_old = request.form.get('password_old', '')
        password_new = request.form.get('password_new', '')
        password_confirm = request.form.get('password_confirm', '')
        user = User.filter(username=username)[0]
        if not user.authenticate(password_old):
            flash('Mật khẩu cũ không đúng', 'error')
        elif password_new != password_confirm:
            flash('Mật khẩu mới không khớp!', 'error')
        else:
            user.edit_pwd(password_new)
            flash('Đổi mật khẩu thành công', 'message')
            return redirect(url_for('login'))
    
    return render_template('edit_password.html')

@app.route('/images/<path:filename>')
def image_file(filename):
    return send_from_directory(IMAGES_ROOT, filename, as_attachment=True)

#---------------------------- Long/Short Polling routes-------------------------------

@app.route('/chat/long', methods=['GET', 'POST'])
@login_required
def long_polling_chat():
    username = request.args.get('username', '')
    room_name = request.args.get('room_name','')
    if request.method == 'GET':
        username = request.args.get('username', '')
        room_name = request.args.get('room_name','')
        # first_time = request.args.get('first_time', '')
        time.sleep(3)
        data = []
        # read data from database
        with open(MESSAGE_DB_DIR,'r') as f:
            while True:
                line = f.readline().strip()
                if not line:
                    break
                user, msg, room, timestamp = line.split(';')
                if room == room_name:
                    data.append({
                        'username':user, 
                        'message': msg,
                        'timestamp': timestamp,
                    })
            f.close()
        return {'messages': data}
    elif request.method == 'POST':
        username = request.form.get('username', '')
        room_name = request.form.get('room_name', '')
        message = request.form.get('message', '')
        timestamp = request.form.get('timestamp', '')
        save_to_database(username, room_name, message, timestamp)
        return {'trang thai': 'ok'}

@app.route('/chat/short', methods=['GET', 'POST'])
@login_required
def short_polling_chat():
    if request.method == 'GET':
        username = request.args.get('username', '')
        room_name = request.args.get('room_name','')
        data = []
        # read data from database
        with open(MESSAGE_DB_DIR,'r') as f:
            while True:
                line = f.readline().strip()
                if not line:
                    break
                user, msg, room, timestamp = line.split(';')
                if room == room_name:
                    data.append({
                        'username':user, 
                        'message': msg,
                        'timestamp': timestamp,
                    })
            f.close()
        return {'messages': data}
    elif request.method == 'POST':
        username = request.form.get('username', '')
        room_name = request.form.get('room_name', '')
        message = request.form.get('message', '')
        timestamp = request.form.get('timestamp', '')
        save_to_database(username, room_name, message, timestamp)
        return {'trang thai': 'ok'}

if __name__ == '__main__':
    print('Server started!')
    socketio.run(app, debug=True)