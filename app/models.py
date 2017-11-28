# -*- coding: utf-8 -*-

import logging
from datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from flask_login import current_user
from sqlalchemy import Column, Integer, String, text

from . import login_manager, db


logger = logging.getLogger(__name__)


class User(db.Model):

    __tablename__ = 'users'

    # Columns

    id = db.Column(db.Integer, primary_key=True, autoincrement=True) # noqa

    username = db.Column(db.String(128)) # noqa

    email = db.Column(db.String(128)) # noqa

    password_hash = db.Column(db.String(1024)) # noqa

    is_admin = db.Column(db.Boolean, default=False) # noqa

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return True

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def get_id(self):
        return self.id

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r %r>' % (self.id, self.username)


@login_manager.user_loader
def load_user(user_id):
    u = User.query.filter_by(username='admin').first()
    current_app.logger.debug('[load_user] user loaded %s, is_authenticated is %s', u, u.is_authenticated)
    return u
