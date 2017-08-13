import logging
from flask import jsonify, make_response, request
from flask_restful import Resource, reqparse
from docker_verify import docker_verify
from models import Answer, db

manager = None

# REST API Endpoints

class AnswerResource(Resource):
    def post(self, task_id):
        ''' Endpoint for submitting code '''
        parser = reqparse.RequestParser()
        parser.add_argument('username', location='args', required=True)
        parser.add_argument('language', location='args', required=True)
        args = parser.parse_args()
        test_cases = manager.get_test_cases(task_id)
        if task_id is None:  # no task exists with the stated id
            return make_response("Tried to respond to an invalid task.", 400)
        # get body of response
        data = request.get_data()

        # verify response using same input
        answer = Answer(
            username=args.username,
            length=len(data),
            correct=docker_verify(data, args.language, test_cases),
            task_id=task_id
        )
        db.session.add(answer)
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
            'latest': Answer.query.filter_by(task_id=task_id).order_by(Answer.created_at.desc()),
            'shortest': Answer.query.filter_by(task_id=task_id).order_by(Answer.length)
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
        logging.error(manager)
        return jsonify(manager.get_tasks())
