from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired
from os import environ

app = Flask(__name__)

# Environment Variables for better configuration
app.config['SECRET_KEY'] = environ.get('SECRET_KEY', 'you-will-never-guess')
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DATABASE_URI', 'sqlite:///data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# User Model Update with Password for Authentication
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False) # Ensure security practices for prod
    tasks = db.relationship('Task', backref='user', lazy=True)

    # Token generation for auth
    def generate_auth_token(self, expiration=600):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id}).decode('utf-8')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token
        user = User.query.get(data['id'])
        return user

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    status = db.Column(db.String(20), default="pending", nullable=False) # New Field for Status
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/api/users', methods=['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400) # missing arguments
    if User.query.filter_by(username=username).first() is not None:
        abort(400) # existing user
    user = User(username=username, password=password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'username': user.username}), 201

@app.route('/api/token', methods=['GET'])
def get_auth_token():
    username = request.json.get('username')
    password = request.json.get('password')
    user = User.query.filter_by(username=username).first()
    if not user or not user.password == password:
        abort(400) # invalid username or password
    token = user.generate_auth_token(600)
    return jsonify({'token': token}), 200

from functools import wraps
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 403
        try:
            current_user = User.verify_auth_token(token)
        except:
            return jsonify({'message': 'Token is invalid!'}), 403
        return f(current_user, *args, **kwargs)
    return decorated_function

@app.route('/api/tasks', methods=['GET'])
@token_required
def get_tasks(current_user):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    tasks = Task.query.filter_by(user_id=current_user.id).paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({'tasks': [{'id': task.id, 'title': task.title, 'description': task.description, 'status': task.status} for task in tasks.items]})

@app.route('/api/tasks', methods=['POST'])
@token_required
def create_task(current_user):
    title = request.json.get('title')
    description = request.json.get('description')
    status = request.json.get('status', 'pending')
    if title is None:
        abort(400) # missing title
    task = Task(title=title, description=description, status=status, user_id=current_user.id)
    db.session.add(task)
    db.session.commit()
    return jsonify({'title': task.title, 'description': task.description, 'status': task.status}), 201

if __name__ == '__main__':
    app.run(debug=True)