import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10

def pageinit_questions(request, selection):
    page_number = request.args.get("page", 1, type=int)
    start_page = (page_number - 1) * QUESTIONS_PER_PAGE
    end_page = start_page + QUESTIONS_PER_PAGE
    return [question.format() for question in selection[start_page:end_page]]

def create_app(test_config=None):
    app = Flask(__name__)
    with app.app_context():
        setup_db(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization,true"
        response.headers["Access-Control-Allow-Methods"] = "GET,PUT,POST,DELETE,OPTIONS"
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response

    @app.route('/categories')
    def get_all_categories():
        categories_data = Category.query.order_by(Category.id).all()
        if not categories_data:
            abort(404)
        return jsonify({
            'success': True,
            'categories': {category.id: category.type for category in categories_data}
        })

    @app.route('/questions')
    def get_all_questions():
        question_data = Question.query.order_by(Question.id).all()
        current_question = pageinit_questions(request, question_data)
        if not current_question:
            abort(404)

        categories = {category.id: category.type for category in Category.query.all()}
        return jsonify({
            'success': True,
            'questions': current_question,
            'total_questions': len(question_data),
            'categories': categories
        })

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question_by_id(question_id):
        question_data = Question.query.get(question_id)
        if not question_data:
            abort(404)
        
        question_data.delete()
        return jsonify({
            'success': True,
            'deleted': question_id,
            'total_questions': len(Question.query.all())
        })

    @app.route('/questions', methods=['POST'])
    def add_question():
        data = request.get_json()
        question_text = data.get('question')
        answer_text = data.get('answer')
        category_id = data.get('category')
        difficulty = data.get('difficulty')

        if not (question_text and answer_text and category_id and difficulty):
            abort(422)

        try:
            question = Question(
                question=question_text,
                answer=answer_text,
                category=category_id,
                difficulty=difficulty
            )
            question.insert()

            selection = Question.query.all()
            current_questions = pageinit_questions(request, selection)
            return jsonify({
                'success': True,
                'created': question.id,
                'questions': current_questions,
                'total_questions': len(selection)
            })
        except:
            abort(422)

    @app.route('/questions/search', methods=['POST'])
    def search_question():
        data = request.get_json().get('searchTerm', '')
        if not data:
            abort(404)
        
        question_data = Question.query.filter(Question.question.ilike(f'%{data}%')).all()
        current_questions = pageinit_questions(request, question_data)
        return jsonify({
            "success": True,
            "questions": current_questions,
            "total_questions": len(question_data)
        })

    @app.route('/categories/<int:category_id>/questions')
    def get_questions_by_category_id(category_id):
        category_data = Category.query.get(category_id)
        if not category_data:
            abort(404)

        question_data = Question.query.filter(Question.category == category_id).all()
        current_questions = pageinit_questions(request, question_data)
        return jsonify({
            "success": True,
            "questions": current_questions,
            "total_questions": len(question_data),
            "current_category": category_data.type
        })

    @app.route('/quizzes', methods=['POST'])
    def start_quiz():
        data = request.get_json()
        category_id = data.get('quiz_category', {}).get('id', 0)
        previous_questions = data.get('previous_questions', [])

        questions_query = Question.query.filter(Question.id.notin_(previous_questions))
        if category_id:
            questions_query = questions_query.filter(Question.category == category_id)
        
        questions = questions_query.all()
        question = random.choice(questions).format() if questions else None
        return jsonify({
            'success': True,
            'question': question
        })

    @app.errorhandler(404)
    def not_found_result(error):
        return jsonify({'success': False, 'error': 404, 'message': 'resource not found'}), 404
    
    @app.errorhandler(422)
    def unprocessable_result(error):
        return jsonify({'success': False, 'error': 422, 'message': 'request cannot be processed'}), 422

    @app.errorhandler(400)
    def bad_request_result(error):
        return jsonify({'success': False, 'error': 400, 'message': 'bad request'}), 400

    @app.errorhandler(405)
    def method_not_allowed_result(error):
        return jsonify({'success': False, 'error': 405, 'message': 'method not allowed'}), 405

    return app
