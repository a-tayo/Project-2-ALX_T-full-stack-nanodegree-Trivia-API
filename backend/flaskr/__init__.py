import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    # CORS headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers', 'Content-Type,Authorization,true'
            )
        response.headers.add(
            'Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS'
        )
        return response

    @app.route('/categories', methods=['GET'])
    def get_all_categories():
        """
        Retrieves all available categories in alphabetical order
        
        Returns: json list of categories
        
        """
        categories = Category.query.order_by('type').all()

        return jsonify({
            'categories': {category.id: category.type for category in categories}
        })

    @app.route('/questions', methods=['GET'])
    def get_questions():
        """
        gets all questions from the database and paginates them
        if method is GET.

        :returns : jsonified questions and categories
        """
        
        page= request.args.get('page', 1, type=int)
        paginated= Question.query.paginate(page, QUESTIONS_PER_PAGE, error_out=False)
        questions = [question.format() for question in paginated.items]

        categories = {category.id: category.type for category in Category.query.order_by('type').all()}
        current_category = categories[2]

        return jsonify({
            'questions': questions,
            'total_questions': paginated.total,
            'categories': categories,
            'current_category': current_category
        })
   
    @app.route('/questions/<int:id>/delete', methods=['DELETE'])
    def delete_questions(id):
        """
        deletes a single question specified by the id from the database
        
        """
        question = Question.query.get_or_404(id)
        try:
            question.delete()
        except:
            abort(422)

        return jsonify({
        'success': True,
        'message': 'deleted successfully'
    })

    @app.route('/questions/create', methods=['POST'])
    def create_questions():
        data = request.get_json() if request.content_type == 'application/json' else None
        if data:
            try:
                question = Question(
                    question = data['question'],
                    answer = data['answer'],
                    category = data['category'],
                    difficulty=data['difficulty']
                )
                question.insert()
            except:
                abort(400)

            return jsonify({
                'success': True,
                'status' : 200
            })
        else:
            abort(400)
            

    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        """
        search for questions based on a given search term
        """
        search_term = request.get_json()['searchTerm']
        results = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
        questions = [result.format() for result in results]

        return jsonify({
            'success': True,
            'questions': questions,
            'total_questions': len(questions),
            'current_category': 2
        })

    @app.route('/categories/<int:id>/questions', methods=['GET'])
    def get_questions_by_category(id):
        """
        get all questions belonging to a specified category

        :params id: the id of the category in the database
        :returns json list of questions
        """
        questions = Question.query.filter(Question.category==id).all()
        formatted_questions = [question.format() for question in questions]
        current_category = Category.query.get(id)

        return jsonify({
            'questions': formatted_questions,
            'current_category': current_category.type
        })

    @app.route('/quizzes', methods=['POST'])
    def play_trivia():
        """
        retrieve questions belonging to a selected category and randomly
        selects one of them as the next question provided it is not present
        in the previous questions.

        returns: random question in the current category
        """
        quizzes = request.get_json()
        previous_questions = quizzes['previous_questions']
        category = quizzes['quiz_category']['id']
        if category:
            questions = Question.query.filter(Question.category == category).all()
        else:
            questions = Question.query.all()

        formatted_questions= [question.format() for question in questions]
        random_question = random.choice(formatted_questions)
        
        while random_question['id'] in previous_questions:
            if len(previous_questions) == len(formatted_questions):
                random_question = None
                break
    
            random_question = random.choice(formatted_questions)
            
        return jsonify({
            'question': random_question
        })

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
                'message': 'not found',
                'error': 404,
                'success': False
                }), 404

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'status': 400,
            'message': 'Your request is not propely formatted.'
        }), 400

    @app.errorhandler(422)
    def uprocessable(error):
        return jsonify({
            'success': False,
            'status': 422,
            'message': 'Your request cannot be processed.'
        }), 422

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'status': 500,
            'message': 'Internal server errror.'
        }), 500

    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
            'success': False,
            'status': 405,
            'message': 'Method not allowed'
        }), 405

    return app

