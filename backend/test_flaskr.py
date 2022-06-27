from http import client
import os
from typing import Dict, List
import unittest
import json
from xml.dom.pulldom import ErrorHandler
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format('student','student', 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    # success

    def test_get_categories_200(self):
        """Test for retrieving the book categories endpoint for success"""
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['categories'])
        self.assertIsInstance(data['categories'], Dict)

    def test_get_questions_200(self):
        """Test the get questions endpoint for success"""
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['total_questions'])
        self.assertIsInstance(data['questions'], List)

    def test_create_questions_200(self):
        """Test the create questions endpoint for success"""
        res = self.client().post('/questions/create', json={"question": "test_question", 
                                                    "answer": "test_answer",
                                                    "category": 3,
                                                    "difficulty": 4})
        data=json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_delete_questions_200(self):
        """Test for a successful deletion"""
        res = self.client().delete('/questions/12/delete')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['message'], 'deleted successfully')

    def test_search_questions_200(self):
        """Test the search questions endpoint for a success"""
        res = self.client().post('/questions/search', json={'searchTerm': 'fantasy'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsInstance(data['questions'], List)
        self.assertIsInstance(data['total_questions'], int)

    # Failures
    def test_delete_questions_404(self):
        """Test for a failed deletion"""
        res = self.client().delete('/questions/400/delete')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['message'], 'not found')

    def test_create_questions_400(self):
        """Test the create questions endpoint for failure"""
        res = self.client().post('/questions/create', json={"question": "test_question", 
                                                    "category": 3,
                                                    "difficulty": 4})
        data=json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data['message'], 'Your request is not propely formatted.')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()