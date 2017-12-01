#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
from flask import (
    render_template, redirect, url_for, abort,
    send_from_directory, current_app, request
)
from flask_login import current_user, login_user
from flask_nav.elements import Navbar, View, Subgroup, Link, Text, Separator
from .forms import LoginForm, LinkCreateForm
from . import main
from .. import db
from .. import login_required
from ..nav import nav
from ..models import User, Link


nav.register_element('frontend_top', Navbar(
    View('Home', '.index'),
    View('Create Link', '.create_link'),
    View('List Link', '.list_link'),
    View('Login', '.login'),
    Text('林克刀客特'), ))


@main.route('/')
def index():
    current_app.logger.info('current_user is %s', current_user)
    current_app.logger.info('current_user.is_authenticated is %s', current_user.is_authenticated)
    if not current_user.is_authenticated:
        return redirect(url_for('main.login'))
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
    for link in links:
        current_app.logger.info(link)
        current_app.logger.info(type(link))
    current_app.logger.info('---------------------------------------')
    current_app.logger.info(type(links))
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
        return redirect(url_for('main.list_link'))
    return render_template('create-link.html', form=form)


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
