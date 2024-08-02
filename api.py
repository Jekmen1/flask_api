from flask import Flask
from flask_restful import Resource, Api, reqparse, abort

app = Flask(__name__)
api = Api(app)

todos = {
    1: {'task': 'write code', 'summary': 'using pycharm'},
    2: {'task': 'task 2', 'summary': 'using pycharm'},
    3: {'task': 'task 3', 'summary': 'using pycharm'}
}

task_post_args = reqparse.RequestParser()
task_post_args.add_argument("task", type=str, help='Task is required', required=True)
task_post_args.add_argument("summary", type=str, help='Summary is required', required=True)

task_put_args = reqparse.RequestParser()
task_put_args.add_argument("task", type=str, help='Task is required')
task_put_args.add_argument("summary", type=str, help='Summary is required')


class HelloWorld(Resource):
    def get(self):
        return {'data': 'Hello, World!'}


class HelloName(Resource):
    def get(self, name):
        return {'data': 'Hello, {}'.format(name)}


class Todo(Resource):
    def get(self, todo_id):
        if todo_id not in todos:
            abort(404, message="Todo ID {} doesn't exist".format(todo_id))
        return todos[todo_id]

    def post(self, todo_id):
        args = task_post_args.parse_args()
        if todo_id in todos:
            abort(409, message="Todo ID {} already exists".format(todo_id))
        todos[todo_id] = {"task": args["task"], "summary": args['summary']}
        return todos[todo_id], 201

    def put(self, todo_id):
        args = task_put_args.parse_args()
        if todo_id not in todos:
            abort(404, message="Todo ID {} doesn't exist".format(todo_id))
        if args['task']:
            todos[todo_id]['task'] = args['task']
        if args['summary']:
            todos[todo_id]['summary'] = args['summary']
        return todos[todo_id]

    def delete(self, todo_id):
        if todo_id not in todos:
            abort(404, message="Todo ID {} doesn't exist".format(todo_id))
        del todos[todo_id]
        return '', 204


class TodoList(Resource):
    def get(self):
        return todos


api.add_resource(Todo, '/todos/<int:todo_id>')
api.add_resource(TodoList, '/todos')
api.add_resource(HelloWorld, '/helloworld')
api.add_resource(HelloName, '/helloworld/<string:name>')


if __name__ == '__main__':
    app.run(debug=True)
