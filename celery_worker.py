#! .env/bin/python
# *-* coding: utf-8 *-*

from celery import Celery
from celery.schedules import crontab
from leadgen import create_app
from leadgen.tasks import log, reverse_messages, create_lead, verify_emails, generate_addresses_for_geocode
from datetime import datetime

time_now = datetime.now()


def create_celery(app):
    celery = Celery(app.import_name,
                    backend=app.config['CELERY_RESULT_BACKEND'],
                    broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery


# create the application
flask_app = create_app()
celery = create_celery(flask_app)


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls reverse_messages every 10 seconds.
    # sender.add_periodic_task(60.0, reverse_messages, name='reverse every 10')
    sender.add_periodic_task(60.0, create_lead, name='Create New Leads')
    sender.add_periodic_task(30.0, verify_emails, name='Verify Lead Emails')
    sender.add_periodic_task(1800.0, generate_addresses_for_geocode, name='Geocode Lead Address')

    # Calls log('Logging Stuff') every 30 seconds
    sender.add_periodic_task(600.0, log.s(('The time is now: {}'.format(time_now.strftime('%c')))), name='Log every 10')

    # Executes every Monday morning at 7:30 a.m.
    sender.add_periodic_task(
        crontab(hour=7, minute=30, day_of_week=1),
        log.s('Monday morning log!'),
    )
