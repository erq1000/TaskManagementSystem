from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import TimedJSONWebSignatureSerializer as TokenSerializer, BadSignature, SignatureExpired
from os import environ
from functools import wraps

app = Flask(__name__)

app.config['SECRET_KEY'] = environ.get('SECRET_KEY', 'default-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DATABASE_URI', 'sqlite:///tasks_database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)
    tasks = db.relationship('Task', backref='assigned_user', lazy=True)

    def generate_token(self, expiration_time=600):
        serializer = TokenSerializer(app.config['SECRET_KEY'], expires_in=expiration_time)
        return serializer.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_token(token):
        serializer = TokenSerializer(app.config['SECRET_KEY'])
        try:
            data = serializer.loads(token)
        except (SignatureExpired, BadSignature):
            return None
        return User.query.get(data['user_id'])

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    completion_status = db.Column(db.String(20), default="pending", nullable=False)
    assigned_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@app.before_first_request
def initialize_database():
    db.create_all()

@app.route('/api/users', methods=['POST'])
def register_user():
    username = request.json.get('username')
    password_hash = request.json.get('password')
    if not username or not password_hash:
        abort(400)
    if User.query.filter_by(username=username).first():
        abort(400)
    new_user = User(username=username, password_hash=password_hash)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'username': new_user.username}), 201

@app.route('/api/token', methods=['GET'])
def obtain_auth_token():
    username = request.json.get('username')
    password_hash = request.json.get('password')
    user = User.query.filter_by(username=username).first()
    if not user or user.password_hash != password_hash:
        abort(400)
    token = user.generate_token(600)
    return jsonify({'authentication_token': token}), 200

def require_token_authentication(protected_function):
    @wraps(protected_function)
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Authentication token is missing!'}), 403
        user = User.verify_token(token)
        if user is None:
            return jsonify({'error': 'Invalid or expired token!'}), 403
        return protected_function(user, *args, **kwargs)
    return wrapper

@app.route('/api/tasks', methods=['GET'])
@require_token_authentication
def fetch_user_tasks(user):
    page_number = request.args.get('page', 1, type=int)
    tasks_per_page = request.args.get('per_page', 20, type=int)
    tasks_query = Task.query.filter_by(assigned_user_id=user.id).paginate(page=page_number, per_page=tasks_per_page, error_out=False)
    tasks = [{'id': task.id, 'title': task.title, 'description': task.description, 'status': task.completion_status} for task in tasks_query.items]
    return jsonify({'tasks': tasks})

@app.route('/api/tasks', methods=['POST'])
@require_token_authentication
def add_new_task(user):
    task_data = request.get_json()
    title = task_data.get('title')
    description = task_data.get('description', '')
    status = task_data.get('status', 'pending')
    if not title:
        abort(400)
    new_task = Task(title=title, description=description, completion_status=status, assigned_user_id=user.id)
    db.session.add(new_task)
    db.session.commit()
    return jsonify({'task': {'title': new_task.title, 'description': new_task.description, 'status': new_task.completion_status}}), 201

if __name__ == '__main__':
    app.run(debug=True)