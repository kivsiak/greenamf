# -*- coding: utf-8 -*-
__author__ = 'kivsiak@gmail.com'

from amfast import class_def
from amfast.class_def.sa_class_def import  SaClassDef
from amfast.remoting import ServiceMapper
from amfast.remoting.sa_connection_manager import SaConnectionManager
from amfast.remoting.sa_subscription_manager import SaSubscriptionManager
from gevent.local import local
from sqlalchemy.engine import create_engine
import sqlalchemy
from werkzeug.exceptions import  HTTPException
import zmq
from greenamf.messaging.channels import StreamingGeventChannel, SecureChannelSet
from greenamf.webapp.auth import AuthRequest



class Node(object):
    def __init__(self, settings):
        self.settings = settings
        self.ctx = zmq.Context()
        self.pub_socket = self.ctx.socket(zmq.PUB)
        self.pub_socket.connect("tcp://127.0.0.1:5001")
        self.paths = {}
        self.initDb()
        self.initServices()
        self.initWeb()
        self.web_context = local()

    def initDb(self):
        self.engine = create_engine(self.settings.database)
        #грязный хак
        self.settings.models[0][0].metadata.create_all(self.engine)
        from sqlalchemy.orm import sessionmaker
        self._sessionFactory= sessionmaker(bind=self.engine)

    @property
    def session(self):
        return  self._sessionFactory()

    def initServices(self):
        connectionManager = SaConnectionManager(self.engine, sqlalchemy.MetaData())
        connectionManager.createTables()
        subscriptionManager = SaSubscriptionManager(self.engine, sqlalchemy.MetaData())
        subscriptionManager.createTables()

        #перенастроить
        self.channelSet = SecureChannelSet(notify_connections=True)
        channel = StreamingGeventChannel("streaming")
        self.channelSet.mapChannel(channel)
        self.channelSet.service_mapper = ServiceMapper()

        for Service in self.settings.services:
            self.channelSet.service_mapper.mapService(Service(self))
        class_mapper = class_def.ClassDefMapper()

        for clazz, alias in self.settings.models:
            class_mapper.mapClass(SaClassDef(clazz, alias))

        channel.endpoint.encoder.class_def_mapper = class_mapper
        channel.endpoint.decoder.class_def_mapper = class_mapper

    def initWeb(self):
        self.url_map = self.settings.urls

    def getHandler(self):
        result = self.__call
        for item in self.settings.middleWares:
            if type(item) == tuple:
                result = item[0](result, *item[1:])
            else:
                result = item(result)
        return  result

    def __call(self, env, start_response):
        if env['PATH_INFO'].startswith("/amf"):
            return self.__amfcall(env, start_response)
        else:
            return self.__webcall(env, start_response)


    def __amfcall(self, env, start_response):
        env['PATH_INFO'] = env['PATH_INFO'][4:]
        self.web_context.env = env
        try:
            return self.channelSet(env, start_response)
        except KeyError:
            start_response('500', [('Content-Type', 'text/html')])
            return  "AMF calls only"

    def __webcall(self, env, start_response):
        try:
            request = AuthRequest(env)
            request.app = self
            request.db = self.session
            adapter = self.url_map.bind_to_environ(request.environ)
            endpoint, values = adapter.match()
            response = endpoint(request, **values)
            return response(env, start_response)
        except HTTPException as e:
            start_response(str(e.code), [('Content-Type', 'text/html')])
            return e




