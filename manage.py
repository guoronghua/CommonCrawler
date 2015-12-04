#!/usr/bin/env python
#coding=utf-8
import os
from app import create_app, db
from app.models import Rule, Node
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand

from datetime import datetime
from twisted.web import http
from twisted.web.wsgi import WSGIResource
from twisted.web.server import Site
from twisted.internet import reactor
from arachne import Arachne

# testing Arachne
app = Arachne(__name__)

resource = WSGIResource(reactor, reactor.getThreadPool(), app)
site = Site(resource,
            logFormatter=http.combinedLogFormatter,
            logPath="logs/"+datetime.now().strftime("%Y-%m-%d.web.log"))
reactor.listenTCP(8080, site)

if __name__ == '__main__':
    reactor.run()


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, Rule=Rule, Node=Node)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == '__main__':
    manager.run()
