from gevent import  monkey

#monkey.patch_all()
from amfast.remoting import ServiceMapper
from amfast.remoting.sa_connection_manager import SaConnectionManager
from amfast.remoting.sa_subscription_manager import SaSubscriptionManager
#import gevent
from sqlalchemy.engine import create_engine
import sqlalchemy
import web
import zmq
from greenamf.messaging.channels import StreamingGeventChannel, SecureChannelSet
from greenamf.services.myService import MyService
from greenamf.webapp.middlewares import StripPathMiddleware

__author__ = 'kivsiak@gmail.com'


class Node(object):
    def __init__(self, config):
        self.config = config
        self.ctx = zmq.Context()
        self.pub_socket = self.ctx.socket(zmq.PUB)
        self.pub_socket.connect("tcp://127.0.0.1:5001")
        self.paths = {}
        self.initDb()
        self.initServices()
        self.initWeb()

    def initDb(self):
        self.engine = create_engine('postgresql+psycopg2://thc:thc@localhost/thc')

    def initServices(self):
        connectionManager = SaConnectionManager(self.engine, sqlalchemy.MetaData())
        connectionManager.createTables()
        subscriptionManager = SaSubscriptionManager(self.engine, sqlalchemy.MetaData())
        subscriptionManager.createTables()

        self.channelSet = SecureChannelSet(notify_connections=True)
        self.channelSet.mapChannel(StreamingGeventChannel("streaming"))
        self.channelSet.service_mapper = ServiceMapper()

        self.channelSet.service_mapper.mapService(MyService(self))


    def initWeb(self):
        urls = (
            '/a', 'greenamf.webapp.views.Index',
            '/longpull', 'greenamf.webapp.views.LongPull',
            '/pull', 'greenamf.webapp.views.Pull'
            )
        self.web_handler = web.application(urls, globals()).wsgifunc()


    def getHandler(self):
        session_opts = {
            'session.type': 'file',
            'session.cookie_expires': 300,
            'session.data_dir': './data',
            'session.auto': True
        }

        return StripPathMiddleware( self.__call)

    def __call(self, env, start_response):
        print env['PATH_INFO']
        if env['PATH_INFO'].startswith("/amf"):
            env['PATH_INFO'] = env['PATH_INFO'][4:]
            try:
                return self.channelSet(env, start_response)
            except KeyError:
                start_response('500', [('Content-Type', 'text/html')])
                return  "AMF calls only"


