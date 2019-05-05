# -*- coding: utf-8 -*-

import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'

    DEBUG = True

    # db
    SQLALCHEMY_DATABASE_URI = "sqlite:///%s/hosts.db" % ( basedir )
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # ldap
    LDAP_HOST = "LDAP地址"
    LDAP_PORT = "LDAP端口"
    MANAGER_DN = "管理账号"
    MANAGER_PASSWORD = "管理密码"
    SEARCH_BASE = "查找dc"


    @staticmethod
    def init_app(app):
        pass

