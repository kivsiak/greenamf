# -*- coding: utf-8 -*-
from beaker.middleware import SessionMiddleware
from werkzeug.debug import DebuggedApplication
from werkzeug.routing import Map, Rule

from greenamf.web.middlewares import StripPathMiddleware
from thc.services import myService
from thc.webapp.views import index, longPull, pull

from domain import  models

__author__ = 'kivsiak@gmail.com'


middleWares = [
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

urls = Map([
    Rule('/', endpoint=index),
    Rule('/long', endpoint=longPull),
    Rule('/pull', endpoint=pull)
])

services = (
    myService.AuthService,
    myService.MyService
    )

database = 'postgresql+psycopg2://thc:thc@localhost/thc'