import logging
import hashlib
from flask import jsonify, make_response, request, redirect, session
from flask_restful import Resource, reqparse
from docker_verify import docker_verify
from models import Answer, User, db
import os

manager = None
tokens = {}
best_answer = None

# Auth URL
AUTH_URL = None

# REST API Endpoints

class AnswerResource(Resource):
    def post(self, task_id):
        ''' Endpoint for submitting code '''
        parser = reqparse.RequestParser()
        parser.add_argument('language', required=True)
        args = parser.parse_args()
        test_cases = manager.get_test_cases(task_id)
        if task_id is None or test_cases is None:  # no task exists with the stated id
            return make_response("Tried to respond to an invalid task.", 400)
        # get user id
        logging.error(session['token'])
        if 'token' not in session or session['token'] not in tokens:
            return make_response("Invalid token.", 400)
        user = db.session.query(User).filter(User.email==tokens[session['token']]).first()

        # get body of response
        data = request.get_data()

        # verify response using same input
        result = docker_verify(data, args.language, test_cases)
        if result is None:
            return make_response("Language is not supported.", 400)
        answer = Answer(
            user_id=user.id,
            task_id=task_id,
            length=len(data),
            correct=all(result),
        )
        db.session.add(answer)
        if all(result):
            if(len(data) < best_answer[task_id][args.language]):
                best_answer[task_id][args.language] = len(data)
        db.session.commit()
        logging.info("%s submitted response to task id %s" %
                     (args.username, task_id))
        return jsonify(answer.to_dict())


class AnswerInfoResource(Resource):
    def get(self, answer_id):
        ''' Endpoint for getting information about a particular answer '''
        answer = Answer.query.filter_by(id=answer_id).first()
        if not answer:
            return make_response("Tried to query an invalid answer.", 400)
        return jsonify(answer.to_dict())


class TaskInfoResource(Resource):
    def get(self, task_id):
        ''' Endpoint for getting information about current state of task '''
        order_queries = {
            'latest': Answer.query
                            .filter_by(task_id=task_id)
                            .order_by(Answer.created_at.desc()),
            'shortest': Answer.query.filter_by(task_id=task_id)
                                    .order_by(Answer.length)
        }
        parser = reqparse.RequestParser()
        parser.add_argument('order', location='args', default='latest')
        args = parser.parse_args()
        task = manager.get_task(task_id)
        if not task:
            return make_response("Tried to query an invalid task.", 400)
        answers = [answer.to_dict()
                   for answer in order_queries[args.order].all()]
        return jsonify({
            'task': task,
            'answers': answers
        })


class TaskListResource(Resource):
    def get(self):
        '''Endpoint for getting a list of all available tasks'''
        tasks = manager.get_tasks()
        retval = []
        for task in tasks:
            retval.append({'name':task['name'],
                           'desc':task['desc']})
        return jsonify(retval)


class LoginResource(Resource):
    def post(self):
        '''Endpoint for getting auth token for existing user'''
        parser = reqparse.RequestParser()
        parser.add_argument('email', required=True)
        parser.add_argument('password', required=True)
        args = parser.parse_args()
        hash_obj = hashlib.sha256()
        hash_obj.update(args.password.encode('utf-8'))
        password_hash = hash_obj.hexdigest()
        user = db.session.query(User).filter((User.email==args.email) & (User.password_hash==password_hash)).first()
        if user is None:
            return 'no account'

        # allocate and maintain session token
        token = os.urandom(256)
        tokens[token] = args.email
        session['token'] = token
        session['username'] = user.username
        return redirect('/')


class SignupResource(Resource):
    def post(self):
        '''Endpoint for registering and getting auth token for new user'''
        parser = reqparse.RequestParser()
        parser.add_argument('username', required=True)
        parser.add_argument('email', required=True)
        parser.add_argument('password', required=True)
        args = parser.parse_args()
        
        # check username and email uniqueness
        duplicate = db.session.query(User).filter((User.username==args.username) | (User.email==args.email)).first()
        if duplicate is not None:
            return redirect('/')

        hash_obj = hashlib.sha256()
        hash_obj.update(args.password.encode('utf-8'))
        user_obj = User(
            username=args.username,
            email=args.email,
            password_hash=hash_obj.hexdigest()
        )
        db.session.add(user_obj)
        db.session.commit()

        # allocate and maintain session token
        token = os.urandom(256)
        tokens[token] = args.email
        session['token'] = token
        session['username'] = args.username
        return redirect('/')
