#!/usr/bin/env python
# -*- coding: utf-8 -*-


DEBUG=True


REDIS_URL = "redis://localhost:6379/0"
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:nst3618mysql@35.187.220.29/link_guard'
# SQLALCHEMY_DATABASE_URI = 'mysql://root:nst3618mysql@35.187.220.29/link_guard'
