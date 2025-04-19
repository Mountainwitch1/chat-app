from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
socketio = SocketIO(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(120), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner = db.Column(db.String(120), nullable=False)
    group_id = db.Column(db.String(120), unique=True, nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('chat'))
        else:
            flash('Invalid username or password!', 'danger')
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists!', 'danger')
        else:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('chat'))
    return render_template('signup.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():
    current_time = datetime.utcnow()
    messages = Message.query.all()

    # Filter out expired messages (older than 12 hours)
    messages = [msg for msg in messages if current_time - msg.timestamp < timedelta(hours=12)]

    return render_template('chat.html', messages=messages, username=current_user.username)


@app.route('/create_group', methods=['POST'])
@login_required
def create_group():
    group_id = str(uuid.uuid4())  # Generates a unique group ID
    new_group = Group(owner=current_user.username, group_id=group_id)
    db.session.add(new_group)
    db.session.commit()
    return redirect(url_for('invite', group_id=group_id))


@app.route('/invite/<group_id>')
def invite(group_id):
    return render_template('invite.html', group_id=group_id)


@socketio.on('send_message')
def handle_message(data):
    msg = Message(user=current_user.username, content=data['message'], timestamp=datetime.utcnow())
    db.session.add(msg)
    db.session.commit()

    # Broadcast message to all users
    emit('receive_message', {
        'user': current_user.username,
        'message': data['message'],
        'timestamp': msg.timestamp.strftime("%H:%M:%S")
    }, broadcast=True)

    # Emit a notification to users if they are not on the chat
    emit('new_message_notification', {
        'message': data['message'],
        'user': current_user.username,
    }, broadcast=True)


if __name__ == '__main__':
    db.create_all()
    socketio.run(app, host="0.0.0.0", port=5001)

