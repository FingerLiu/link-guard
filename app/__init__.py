#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from celery import Celery
from flask import current_app, Flask, render_template, redirect, request, url_for
from flask_login import LoginManager, current_user
from flask_redis import FlaskRedis
from flask_sqlalchemy import SQLAlchemy
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


login_manager = LoginManager()
login_manager.login_view = 'auth.login'
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
    redis_store.init_app(app)
    login_manager.init_app(app)
    make_celery(celery, app)
    return app


app = create_app()


@celery.task()
def add_together(a, b):
    return a + b
