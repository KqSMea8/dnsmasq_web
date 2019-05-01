import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'

    DEBUG = True

    # db
    SQLALCHEMY_DATABASE_URI = "sqlite:///%s/hosts.db" % ( basedir )
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    @staticmethod
    def init_app(app):
        pass

