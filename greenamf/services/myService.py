import gevent

__author__ = 'kivsiak@gmail.com'

from greenamf.messaging.decorators import operation, RPCService, Service

@Service('myService')
class MyService(RPCService):
    def __init__(self, app):
        super(MyService, self).__init__()
        self.app = app

    @operation("returnTrue")
    def operationA(self):
        gevent.sleep(1000)
        return True

    @operation("echo")
    def operationB(self, arg):
        return arg

