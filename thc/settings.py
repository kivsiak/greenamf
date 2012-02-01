# -*- coding: utf-8 -*-
from beaker.middleware import SessionMiddleware
from werkzeug.debug import DebuggedApplication
from werkzeug.routing import Map, Rule
from greenamf.domain.models import getExposed
from greenamf.webapp.middlewares import StripPathMiddleware
from thc.domain import models
from thc.services import myService
from thc.webapp.views import index, longPull, pull

__author__ = 'kivsiak@gmail.com'

class DotDict(dict):
    def __getattr__(self, attr):
        return self.get(attr, None)

    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

settings = DotDict()

settings.middleWares = [
    DebuggedApplication,
    StripPathMiddleware,
    (SessionMiddleware, {
        'session.type': 'file',
        'session.cookie_expires': 300,
        'session.data_dir': './data',
        'session.auto': True,
        'session.key': 'session_id'
    })
]

settings.urls = Map([
    Rule('/', endpoint=index),
    Rule('/long', endpoint=longPull),
    Rule('/pull', endpoint=pull)
])

settings.services = (
    myService.AuthService,
    myService.MyService
    )

settings.models =  getExposed(models)



settings.database = 'postgresql+psycopg2://thc:thc@localhost/thc'