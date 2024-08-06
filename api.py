from flask import Flask, request, jsonify
from flask_restful import Resource, Api, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_bcrypt import Bcrypt
import logging


logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
bcrypt = Bcrypt(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class ToDoModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(200))
    summary = db.Column(db.String(500))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_tables():
    db.create_all()


task_post_args = reqparse.RequestParser()
task_post_args.add_argument("task", type=str, help='Task is required', required=True)
task_post_args.add_argument("summary", type=str, help='Summary is required', required=True)

task_put_args = reqparse.RequestParser()
task_put_args.add_argument("task", type=str, help='Task is required')
task_put_args.add_argument("summary", type=str, help='Summary is required')

user_post_args = reqparse.RequestParser()
user_post_args.add_argument("username", type=str, help='Username is required', required=True)
user_post_args.add_argument("password", type=str, help='Password is required', required=True)

resource_fields = {
    'id': fields.Integer,
    'task': fields.String,
    'summary': fields.String
}

# User Registration
class Register(Resource):
    def post(self):
        args = user_post_args.parse_args()
        hashed_password = bcrypt.generate_password_hash(args['password']).decode('utf-8')
        user = User(username=args['username'], password=hashed_password)
        db.session.add(user)
        db.session.commit()
        return jsonify(message="User registered successfully")


class Login(Resource):
    def post(self):
        args = user_post_args.parse_args()
        user = User.query.filter_by(username=args['username']).first()
        if user and bcrypt.check_password_hash(user.password, args['password']):
            login_user(user)
            return jsonify(message="Logged in successfully")
        return abort(401, message="Invalid credentials")


class Logout(Resource):
    @login_required
    def post(self):
        logout_user()
        return jsonify(message="Logged out successfully")

class TodoList(Resource):
    @login_required
    @marshal_with(resource_fields)
    def get(self):
        tasks = ToDoModel.query.filter_by(user_id=current_user.id).all()
        return tasks

class ToDo(Resource):
    @login_required
    @marshal_with(resource_fields)
    def get(self, todo_id):
        task = ToDoModel.query.filter_by(id=todo_id, user_id=current_user.id).first()
        if not task:
            abort(404, message="Todo ID {} doesn't exist".format(todo_id))
        return task

    @login_required
    @marshal_with(resource_fields)
    def post(self, todo_id):
        args = task_post_args.parse_args()
        task = ToDoModel.query.filter_by(id=todo_id, user_id=current_user.id).first()
        if task:
            abort(409, message="Todo ID {} already exists".format(todo_id))

        todo = ToDoModel(id=todo_id, task=args['task'], summary=args['summary'], user_id=current_user.id)
        db.session.add(todo)
        db.session.commit()
        return todo, 201

    @login_required
    @marshal_with(resource_fields)
    def put(self, todo_id):
        args = task_put_args.parse_args()
        task = ToDoModel.query.filter_by(id=todo_id, user_id=current_user.id).first()
        if not task:
            abort(404, message="Todo ID {} doesn't exist".format(todo_id))

        if args['task']:
            task.task = args['task']
        if args['summary']:
            task.summary = args['summary']

        db.session.commit()
        return task

    @login_required
    @marshal_with(resource_fields)
    def delete(self, todo_id):
        task = ToDoModel.query.filter_by(id=todo_id, user_id=current_user.id).first()
        if not task:
            abort(404, message="Todo ID {} doesn't exist".format(todo_id))
        db.session.delete(task)
        db.session.commit()
        return '', 204

api.add_resource(Register, '/register')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(ToDo, '/todos/<int:todo_id>')
api.add_resource(TodoList, '/todos')

if __name__ == '__main__':
    with app.app_context():
        create_tables()
    app.run(debug=True)

