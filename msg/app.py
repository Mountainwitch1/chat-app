from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_socketio import SocketIO, emit
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
socketio = SocketIO(app)
login_manager = LoginManager()
login_manager.init_app(app)

# Track online users
online_users = set()

from models import User, Message

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.password == request.form['password']:
            login_user(user)
            return redirect(url_for('chat'))
        flash('Invalid login')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user = User(username=request.form['username'], password=request.form['password'])
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('chat'))
    return render_template('signup.html')

@app.route('/chat')
@login_required
def chat():
    messages = Message.query.order_by(Message.timestamp).all()
    return render_template('chat.html', messages=messages, username=current_user.username)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@socketio.on('connect')
def handle_connect():
    if current_user.is_authenticated:
        online_users.add(current_user.username)
        emit('user_status', {'user': current_user.username, 'status': 'online'}, broadcast=True)
        emit('online_users', list(online_users))

@socketio.on('disconnect')
def handle_disconnect():
    if current_user.is_authenticated:
        online_users.discard(current_user.username)
        emit('user_status', {'user': current_user.username, 'status': 'offline'}, broadcast=True)

@socketio.on('send_message')
def handle_message(data):
    msg = Message(user=current_user.username, content=data['message'], timestamp=datetime.utcnow())
    db.session.add(msg)
    db.session.commit()
    emit('receive_message', {
        'user': current_user.username,
        'message': data['message'],
        'timestamp': msg.timestamp.strftime("%H:%M:%S")
    }, broadcast=True)

@socketio.on('typing')
def handle_typing(data=None):
    emit('user_typing', {'user': current_user.username}, broadcast=True, include_self=False)

if __name__ == '__main__':
    db.create_all()
    socketio.run(app, port=8000, debug=True)
