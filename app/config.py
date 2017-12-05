#!/usr/bin/env python
# -*- coding: utf-8 -*-


SECRET_KEY = 'fdsf3vzzv09szv9ssfsawf32dsffasasdf233sd'
DEBUG=True


REDIS_URL = "redis://localhost:6379/0"
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERYD_MAX_TASKS_PER_CHILD = 1

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:nst3618mysql@35.187.220.29/link_guard'
# SQLALCHEMY_DATABASE_URI = 'mysql://root:nst3618mysql@35.187.220.29/link_guard'
CDN = 'https://sstatic.qrpay.paduola.com/'

DEPTH_LIMIT = 3
