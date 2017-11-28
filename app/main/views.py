#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import (
    render_template, redirect, url_for, abort,
    send_from_directory, current_app, request
)
from flask_login import current_user
from ..auth.forms import LoginForm
from ..utils import logged
from . import main
from .. import login_required
from .forms import TestMultiFileFieldForm


@main.route('/')
@logged()
def index():
    current_app.logger.info('current_user is %s', current_user)
    current_app.logger.info('current_user.is_authenticated is %s', current_user.is_authenticated)
    if current_user.is_authenticated:
        return redirect(url_for('auth.profile'))
    else:
        return redirect(url_for('main.landing'))


@main.route('/landing/', methods=['GET'])
def landing():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    return render_template('landing.html', form=form)
