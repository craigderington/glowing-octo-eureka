### Celery Lead Generator
Celery Task Queue to Process and Data Mine Lead Data

Featuring:

- App factory with setup
- Periodic tasks and cron schedule with celery heartbeat
- Flask cli script for an ipython shell and url_map

#### Installating the app

Configure Dependencies

```
sudo apt install python3 python3-pip mysql-server rabbitmq-server redis-server
libmysqlclient-dev python-imaging python-dev python-setuptools
```


#### Create virtual environment
```shell
virtualenv .env --python=python3
. .env/bin/activate
pip install -r requirements.txt
```

#### Start RabbitMQ Message Broker on System Startup
```shell
sudo systemctl enable rabbitmq-server
```

#### Start Celery Worker(s)
```
celery -A celery_worker:celery worker --loglevel=DEBUG
```

#### Start Celery Heartbeat for Periodic Tasks
```
celery -A celery_worker:celery beat --loglevel=INFO
```

#### Start Flask App for Task Messaging Status
```shell
env 'FLASK_APP=manage.py' flask run
```

#### Monitor the Task Queue

Run from activated virtual environment

```
celery flower leadgen.app.celery
```


#### Access the RabbitMQ Management Server

Browse to https://localhost:15672

Login required.
