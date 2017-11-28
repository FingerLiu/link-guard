#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from app import app, db


manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)


from app import models


if __name__ == '__main__':
    manager.run()
