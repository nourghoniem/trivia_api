import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE
  questions = [question.format() for question in selection]
  question_samples = questions[start:end]
  return question_samples

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
   response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
   response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
   return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories', methods=['GET'])
  def get_categories():
     categories = Category.query.order_by(Category.id).all()
     all_categories = {}
     for category in categories:
       all_categories[category.id] = category.type
     if(len(all_categories) == 0):
       abort(404)
     return jsonify({
       'success': True,
       'categories': all_categories,
     })
     
  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions', methods=['GET'])
  def get_questions():
    try: 
      selection = Question.query.order_by(Question.id).all()
      categories = Category.query.order_by(Category.id).all()
      questions = paginate_questions(request, selection)
      all_categories = {}
      for category in categories:
        all_categories[category.id] = category.type
      if(len(questions) == 0):
        abort(404)
      return jsonify({
        'success': True,
        'questions': questions,
        'total_questions': len(Question.query.all()),
        'categories': all_categories,
       })
    except:
      abort(404)

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
       question = Question.query.filter(Question.id == question_id).one_or_none()
       if question is None:
         abort(404)
       question.delete()
       selection = Question.query.order_by(Question.id).all()
       questions = paginate_questions(request, selection)
       return jsonify({
          'success': True,
          'questions': questions,
          'total_questions': len(Question.query.all()),
         })
    except:
        abort(422)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
 
  @app.route('/questions', methods=['POST'])
  def insert_question():
     body = request.get_json()
     question = body.get('question', None)
     answer = body.get('answer', None)
     category = body.get('category', None)
     difficulty = body.get('difficulty', None)
     search = body.get('searchTerm', None)
     try:
        if search:
           selection = Question.query.order_by(Question.id).filter(Question.question.ilike(f'%{search}%')).all()
           questions = paginate_questions(request, selection)
           return jsonify({
            'success': True,
            'questions': questions,
            'total_questions': len(Question.query.all()),
           })
        else:
          new_question = Question(question=question, answer=answer, category= category, difficulty=difficulty)
          new_question.insert()
          selection = Question.query.order_by(Question.id).all()
          questions = paginate_questions(request, selection)
          return jsonify({
            'success': True,
            'questions': questions,
            'total_questions': len(Question.query.all()),
           })
     except:
        abort(422)

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<string:category_id>/questions')
  def get_questions_by_categories(category_id):
     category = Category.query.filter(Category.id == category_id).one_or_none()
     if category is None:
      abort(400)
     questions = Question.query.filter(Question.category == category_id).all()
     if(len(questions) == 0):
      abort(404)
     return jsonify({
        'success': True,
        'questions': [question.format() for question in questions],
        'total_questions': len(Question.query.all()),
        'current_category': category_id,
        })

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def get_questions_quiz():
      body = request.get_json()
      category = body.get('category')
      previous_questions = body.get('previous_questions')
      if category is None or previous_questions is None:
       abort(400)
      if (category['id'] == 0):
        questions = Question.query.filter(Question.id.notin_(previous_questions)).order_by(Question.id).all()
      else:
        questions = Question.query.filter_by(category = category["id"]).filter(Question.id.notin_(previous_questions)).order_by(Question.id).all()
        random_question = questions[random.randint(0, len(questions)-1)]
      return jsonify({
         'success':True,
         'question': random_question.format(),
       })

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(400)
  def bad_request(error):
      return jsonify ({
            "success" : False,
            "error": 400,
            "message": "bad request",         
        }), 400

  @app.errorhandler(404)
  def not_found(error):
        return jsonify ({
            "success" : False,
            "error": 404,
            "message": "resource not found",         
        }), 404

  @app.errorhandler(405)
  def methodnotallowed(error):
      return jsonify ({
            "success" : False,
            "error": 405,
            "message": "method not allowed",         
        }), 405
        
  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify ({
            "success" : False,
            "error": 422,
            "message": "unprocessable",         
        }), 422
  
  return app

    