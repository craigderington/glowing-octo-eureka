import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    SECRET_KEY = '$really@super!secretkey%'

    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://username:password@localhost:3306/leadgen'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', SQLITE_DB)

    CELERY_TIMEZONE = 'US/Eastern'
    CELERY_BROKER_URL = 'amqp://localhost/'
    CELERY_RESULT_BACKEND = 'rpc://'
    CELERY_SEND_TASK_SENT_EVENT = True


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    pass


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
