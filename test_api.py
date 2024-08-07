import unittest
from api import app, db, User, ToDoModel
from flask_bcrypt import generate_password_hash


class FlaskTestCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        app.config['TESTING'] = True
        self.app = app.test_client()
        with app.app_context():
            db.create_all()

            # Create a test user
            hashed_password = generate_password_hash('testpassword').decode('utf-8')
            user = User(username='testuser', password=hashed_password)
            db.session.add(user)
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.drop_all()

    def test_user_registration(self):
        response = self.app.post('/register', json={
            'username': 'newuser',
            'password': 'newpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('User registered successfully', response.json['message'])

    def test_user_login(self):
        response = self.app.post('/login', json={
            'username': 'testuser',
            'password': 'testpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('Logged in successfully', response.json['message'])

    def test_user_login_invalid_credentials(self):
        response = self.app.post('/login', json={
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 401)

    def test_todo_creation(self):
        self.app.post('/login', json={
            'username': 'testuser',
            'password': 'testpassword'
        })

        response = self.app.post('/todos/1', json={
            'task': 'Test Task',
            'summary': 'Test Summary'
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn('Test Task', response.json['task'])

    def test_todo_creation_duplicate_id(self):
        self.app.post('/login', json={
            'username': 'testuser',
            'password': 'testpassword'
        })

        self.app.post('/todos/1', json={
            'task': 'Test Task',
            'summary': 'Test Summary'
        })

        response = self.app.post('/todos/1', json={
            'task': 'Duplicate Task',
            'summary': 'Duplicate Summary'
        })
        self.assertEqual(response.status_code, 409)

    def test_todo_retrieval(self):
        self.app.post('/login', json={
            'username': 'testuser',
            'password': 'testpassword'
        })

        self.app.post('/todos/1', json={
            'task': 'Test Task',
            'summary': 'Test Summary'
        })

        response = self.app.get('/todos/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Test Task', response.json['task'])

    def test_todo_update(self):
        self.app.post('/login', json={
            'username': 'testuser',
            'password': 'testpassword'
        })

        self.app.post('/todos/1', json={
            'task': 'Test Task',
            'summary': 'Test Summary'
        })

        response = self.app.put('/todos/1', json={
            'task': 'Updated Task',
            'summary': 'Updated Summary'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('Updated Task', response.json['task'])

    def test_todo_deletion(self):
        self.app.post('/login', json={
            'username': 'testuser',
            'password': 'testpassword'
        })

        self.app.post('/todos/1', json={
            'task': 'Test Task',
            'summary': 'Test Summary'
        })

        response = self.app.delete('/todos/1')
        self.assertEqual(response.status_code, 204)


if __name__ == '__main__':
    unittest.main()
