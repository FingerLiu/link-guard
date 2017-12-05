#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from functools import wraps
from celery import Celery
from flask import current_app, Flask, render_template, redirect, request, url_for
from flask_login import LoginManager, current_user
from flask_redis import FlaskRedis
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap, WebCDN
from . import config
from . import link_guard


def make_celery(celery, app):
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    celery.autodiscover_tasks(['link_guard'])
    return celery


def login_required(func):
    '''
    :param func: The view function to decorate.
    :type func: function
    '''
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if request.method in set(['OPTIONS']):
            return func(*args, **kwargs)
        elif current_app.login_manager._login_disabled:
            return func(*args, **kwargs)
        elif not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()
        elif getattr(current_user, 'status', None) == 'draft':
            return current_app.login_manager.not_complete()
        return func(*args, **kwargs)
    return decorated_view


login_manager = LoginManager()
bootstrap = Bootstrap()
login_manager.login_view = 'main.login'
redis_store = FlaskRedis()
db = SQLAlchemy()
celery = Celery(
    'link_guard', backend=config.CELERY_RESULT_BACKEND,
    broker=config.CELERY_BROKER_URL
)


def create_app(debug=True):
    app = Flask(__name__)
    app.config.from_object(config)
    app.debug = debug
    db.init_app(app)
    bootstrap.init_app(app)
    redis_store.init_app(app)
    login_manager.init_app(app)
    make_celery(celery, app)
    app.extensions['bootstrap']['cdns']['jquery'] = WebCDN(app.config['CDN'])
    app.extensions['bootstrap']['cdns']['bootstrap'] = WebCDN(app.config['CDN'])

    from .main import main
    app.register_blueprint(main)
    return app


app = create_app()


celery.task()
def add_together(a, b):
    return a + b
