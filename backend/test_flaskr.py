import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category
from sqlalchemy import create_engine
from dotenv import load_dotenv

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        load_dotenv()

        # Initialize the app and client
        self.app = create_app()
        self.client = self.app.test_client()

        # Load test database configuration from .env
        db_host = os.getenv("DB_HOST")
        db_port = os.getenv("DB_PORT")
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        db_name = os.getenv("DB_NAME")

        # Construct the test database URL
        self.database_path = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        
        # Example: create a connection (if necessary)
        self.engine = create_engine(self.database_path)
        setup_db(self.app, self.database_path)

    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    ## /categories
    def test_get_category(self):
        result = self.client().get('/categories')
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertEqual(data['success'], True)
        
    ## /questions
    def test_get_questions(self):
        result = self.client().get('/questions')
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertEqual(data['success'], True)
        
    ## /questions/<int:question_id> DELETE 
    def test_question_for_delete(self):
        result = self.client().delete('/questions/100')
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 404)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["message"], "success")
        
    def test_question_for_delete_not_found(self):
        result = self.client().delete('/questions/60000')
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Page not found")
    
    ## /questions POST
    def test_question_for_insert(self):
        question = {
            'question': 'What are your favorite?',
            'answer': 'Eat',
            'difficulty': 0,
            'category': 1
        }
        result = self.client().post('/questions', json=question)
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["message"], "success")
        
    ## /questions/search POST
    def test_question_for_search(self):
        promt = {'searchTerm': 'favorite', }
        result = self.client().post('/questions/search', json=promt)
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 12)
        
    ## /categories/<int:category_id>/questions
    def test_get_questions_by_category_id(self):
        result = self.client().get('/categories/4/questions')
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertNotEqual(len(data['questions']), 0)
        self.assertEqual(data["message"], "success")
           
    ## /quizzes
    def test_get_quiz(self):
        quiz = {
            'quiz_category': {
                'type': 'Art',
                'id': '2'
            }
        }
        result = self.client().post('/quizzes', json=quiz)
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['question']['category'], '2')
    
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()