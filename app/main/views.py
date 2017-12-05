#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
from werkzeug.security import generate_password_hash
from flask import (
    render_template, redirect, url_for, abort,
    send_from_directory, current_app, request
)
from flask_login import current_user, login_user, logout_user
from app.link_guard.tasks import guard
from .forms import LoginForm, LinkCreateForm, RegistrationForm
from . import main
from .. import db
from .. import login_required
from ..models import User, Link


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/list-link/', methods=['GET'])
@login_required
def list_link():
    def obj2dict(obj):
        dic = obj.__dict__
        dic.pop('_sa_instance_state')
        return dic

    links = Link.query.filter_by(owner_id=current_user.id)
    links = [obj2dict(link) for link in links]
    columns = [
        {
            "field": "domain",
            "title": "domain",
        },
        {
            "field": "start_url",
            "title": "start_url",
        },
        {
            "field": "broken_links",
            "title": "broken_links",
        },
        {
            "field": "status",
            "title": "status",
        }
    ]
    return render_template('list-link.html', data=links, columns=columns)


@main.route('/create-link/', methods=['GET', 'POST'])
@login_required
def create_link():
    form = LinkCreateForm()
    if form.validate_on_submit():
        link = Link(
            domain=form.domain.data,
            start_url=form.start_url.data,
            last_check_datetime=datetime.datetime.now(),
            owner_id=current_user.id
        )
        db.session.add(link)
        db.session.commit()

        task = guard.delay(**{'domain': form.domain.data, 'start_url': form.start_url.data})

        return redirect(url_for('main.list_link'))
    return render_template('create-link.html', form=form)


@main.route('/link/<domain>/')
@login_required
def show_link():
    link = Link.query.filter_by(domain=domain).first()
    return render_template('link.html', link=link)


@main.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        current_app.logger.info('user %s try to login', form.email.data)
        current_app.logger.debug('query from sql is %s', user)
        login_user(user, True)
        return redirect(request.args.get('next') or url_for('main.index'))
    return render_template('login.html', form=form)


@main.route('/register/', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        password_hash = generate_password_hash(form.password.data)
        user = User(
            email=form.email.data,
            username=form.username.data,
            password_hash=password_hash,
            create_datetime=datetime.datetime.now(),
        )
        db.session.add(user)
        db.session.commit()

        login_user(user, True)
        return redirect(request.args.get('next') or url_for('main.index'))
    return render_template('registeration.html', form=form)


@main.route('/logout/')
def logout():
    logout_user()
    return redirect(url_for('main.login'))
