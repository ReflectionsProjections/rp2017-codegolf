import logging
import hashlib
from flask import jsonify, make_response, request, redirect, session
from flask_restful import Resource, reqparse
from docker_verify import docker_verify
from models import Answer, User, db
from task_manager import TaskManager
import os

# Challenge data file URL
CHALLENGES_PATH = 'data/challenges.json'

# Static variables
manager = TaskManager(CHALLENGES_PATH)
best_answer = [{
    'cc':float('inf'), 
    'java':float('inf'), 
    'js':float('inf'), 
    'py':float('inf')} for _ in manager.get_tasks()]
tokens = {}

# REST API Endpoints

class AnswerResource(Resource):
    def post(self, task_id):
        ''' Endpoint for submitting code '''
        parser = reqparse.RequestParser()
        parser.add_argument('language', required=True)
        parser.add_argument('code', required=True)
        args = parser.parse_args()
        task = manager.get_task(task_id)
        if task_id is None or task is None:  # no task exists with the stated id
            return redirect('/?task=%d&message=%s' % (task_id, 'task does not exist.'))
        test_cases = task.get('test_cases', None)
        # get user id
        if 'token' not in session or session['token'] not in tokens:
            return redirect('/?task=%d&message=%s' % (task_id, 'invalid token supplied.'))
        user = db.session.query(User).filter(User.email==tokens[session['token']]).first()

        # verify response using same input
        result = docker_verify(args.code, args.language, test_cases)
        if result is None:
            return redirect('/?task=%d&message=%s' % (task_id, 'language is not supported'))
        if all(result):
            if(len(args.code) < best_answer[task_id][args.language]):
                best_answer[task_id][args.language] = len(args.code)
            max_points = int(task.get('points', None))
            points = max_points * best_answer[task_id][args.language]/len(args.code)

            # look for better answer from same user
            prev_answer = db.session.query(Answer).filter((Answer.user_id==user.id) & (Answer.task_id==task_id) & (Answer.points>points)).first()
            if prev_answer is None:
                answer = Answer(
                    user_id=user.id,
                    task_id=task_id,
                    length=len(args.code),
                    points=points,
                    language=args.language
                )
                db.session.add(answer)
                user.points = sum([answer.points for answer in user.answers])
                db.session.commit()
        return redirect('/')


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
            return redirect('/?message=%s' % 'Could not find account.')

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
            return redirect('/?message=%s' % 'Account already exists for this email.')

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
