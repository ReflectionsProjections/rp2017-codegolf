# -*- coding: utf-8 -*-

from flask import Flask, jsonify, make_response, render_template
import flask
import json
import os
from datetime import datetime
import time
from subprocess import Popen, PIPE
import requests
import logging
import hashlib
from flask_restful import Resource, Api, reqparse
from models import Task, Answer, db

app = Flask(__name__)
app.config['JSONIFY_MIMETYPE'] = 'application/json; charset=UTF-8'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

PORT = 21337

api = Api(app)

# REST API Endpoints

class AnswerResource(Resource):
    def post(self, task_id):
        ''' Endpoint for submitting code '''
        parser = reqparse.RequestParser()
        parser.add_argument('answer', location='args', required=True)
        parser.add_argument('timestamp', location='args', required=True)
        parser.add_argument('length', location='args', required=True)
        parser.add_argument('username', location='args', required=True)
        args = parser.parse_args()
        task = Task.query.filter_by(id=task_id).first()
        if not task: # no task exists with the stated id
            return make_response("Tried to respond to an invalid task.", 400)
        # verify response using same input
        time_hash = hexdigest(args.timestamp)
        correct_answer = str(get_correct_answer(time_hash, task.test_link, task.answer_link))
        correct_hash = str(hexdigest(correct_answer))
        answer = Answer(
            username = args.username,
            length = args.length,
            correct = args.answer == correct_hash,
            task_id = task_id
        )
        db.session.add(answer)
        db.session.commit()
        logging.info("%s submitted response to task id %s" % (args.username, task_id))
        return jsonify(answer.to_dict())

class AnswerInfoResource(Resource):
    def get(self, answer_id):
        ''' Endpoint for getting information about a particular answer '''
        answer = Answer.query.filter_by(id=answer_id).first()
        if not answer:
            return make_response("Tried to query an invalid answer.", 400)
        return jsonify(answer.to_dict())

class TaskResource(Resource):
    def post(self):
        ''' Endpoint for submitting tasks '''
        parser = reqparse.RequestParser()
        parser.add_argument('name', location='args', required=True)
        parser.add_argument('desc_link', location='args', required=True)
        parser.add_argument('test_link', location='args', required=True)
        parser.add_argument('answer_link', location='args', required=True)
        args = parser.parse_args()
        # TODO (warut-vijit): verify file existence for links
        if Task.query.filter_by(name=args.name).first():
            return make_response("Tried to create a task with duplicate name %s" % args.name)
        task = Task(
            name = args.name,
            desc_link = args.desc_link,
            test_link = args.test_link,
            answer_link = args.answer_link
        )
        db.session.add(task)
        db.session.commit()
        return jsonify(task.to_dict())

class TaskInfoResource(Resource):
    def get(self, task_id):
        ''' Endpoint for getting information about current state of task '''
        order_queries = {
            'latest': Answer.query.filter_by(task_id=task_id).order_by(Answer.created_at.desc()),
            'shortest': Answer.query.filter_by(task_id=task_id).order_by(Answer.length)
        }
        parser = reqparse.RequestParser()
        parser.add_argument('order', location='args', default='latest')
        args = parser.parse_args()
        task = Task.query.filter_by(id=task_id).first()
        if not task:
            return make_response("Tried to query an invalid task.", 400)
        answers = [answer.to_dict() for answer in order_queries[args.order].all()]
        try:
            desc = open(task.desc_link).read()
        except IOError:
            desc = 'No description exists for this task. :('
        try:
            test = open(task.test_link).read()
        except IOError:
            test = 'No test exists for this task. :('
        return jsonify({
            'task': task.to_dict(),
            'answers': answers,
            'desc': desc,
            'test': test
        })

class TaskListResource(Resource):
    def get(self):
        '''Endpoint for getting a list of all available tasks'''
        tasks = [task.to_dict() for task in Task.query.all()]
        return jsonify(tasks)


# hashing function, returns bytes
def hexdigest(string):
    hashobj = hashlib.sha256()
    hashobj.update(bytes(string, 'utf-8'))
    return hashobj.digest()

# testing function. Takes hash as test case, test file and answer file from task object
# returns answer for test case specified by hash
def get_correct_answer(data, test_file, answer_file):
    try:
        answer = open(answer_file).read()
        with open('answer.py', 'w') as temp:
            temp.write(answer)
        test = open(test_file).read()
        with open('test.py', 'w') as temp:
            temp.write(test)
        import test
        test_result = test.test(data)
        os.remove('answer.py')
        os.remove('test.py')
        return test_result
    except IOError:
        raise IOError('Malformed testing files for %s' % test_file)
        

api.add_resource(TaskListResource, '/golf/task_list')
api.add_resource(AnswerResource, '/golf/<int:task_id>/answer')
api.add_resource(AnswerInfoResource, '/golf/<int:answer_id>/answer_info')
api.add_resource(TaskResource, '/golf/task')
api.add_resource(TaskInfoResource, '/golf/<int:task_id>/task_info')
db.app = app
db.init_app(app)
db.create_all(app=app)

if __name__ == '__main__':
    logging.basicConfig(level="INFO")
    app.run(host='0.0.0.0', port=PORT, debug=True, threaded=True)
