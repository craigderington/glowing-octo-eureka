from datetime import datetime, timedelta

from flask import Blueprint, jsonify, url_for, render_template

from leadgen import db
from leadgen.models import Message
from leadgen.tasks import long_task

home = Blueprint('home', __name__)


@home.before_app_first_request
def init_db():
    db.create_all()


@home.route('/', methods=['GET'])
def longtask():
    """add a new task and start running it after 10 seconds"""
    eta = datetime.utcnow() + timedelta(seconds=10)
    task = long_task.apply_async(eta=eta)
    _link = url_for('home.taskstatus', task_id=task.id, _external=True)

    return render_template(
        'index.html',
        link=_link,
        task=task,
        eta=eta
    )


@home.route('/status/<task_id>/', methods=['GET'])
def taskstatus(task_id):
    task = long_task.AsyncResult(task_id)
    if task.state == 'PENDING':
        # job did not start yet
        response = {
            'state': task.state,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)


@home.route('/messages/')
def messages():
    messages = Message.query.all()
    return jsonify([message.text for message in messages])
