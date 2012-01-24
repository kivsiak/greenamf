# -*- coding: utf-8 -*-
from amfast import remoting
from gevent.local import local

__author__ = 'kivsiak@gmail.com'


def operation(name, auth = False):
    def realDecorator(f):
        f.name = name
        f.secure = False
        f.operation = True
        return f
    return realDecorator




def Service(name):
    def realDecorator(obj):
        obj.name = name
        obj.service = True
        return obj
    return  realDecorator


class Context(object):
    def get(self ):
        pass



class RPCServiceBase(type):
    def __new__(cls, name, bases, attrs):
        super_new = super(RPCServiceBase, cls).__new__
        parents = [b for b in bases if isinstance(b, RPCServiceBase)]
        if not parents:
            # If this isn't a subclass of Model, don't do anything special.
            return super_new(cls, name, bases, attrs)
        attrs['operations'] = {}
        for key, attr in attrs.items():
            if hasattr(attr, '__call__') and hasattr(attr, 'operation'):
                attrs['operations'][attr.name] = attr
                def methodError(self):
                    raise NotImplementedError("%s cannot be called directly" % key)
                attrs[key] = methodError
        return super_new(cls, name, bases, attrs)

def mine(self):
        pass

class RPCService(remoting.Service):
    __metaclass__ = RPCServiceBase

    def __init__(self):
        self.context = local()
        super(RPCService, self).__init__(self.name)
        for name, method in self.operations.items():
            self.mapTarget(remoting.ExtCallableTarget(Wrapper(self, method), name, secure=method.secure))

    def callRPCMethod(self, method , packet, msg,  *args):
        self.context.packet = packet
        self.context.msg = msg
        return method(self, *args)


class Wrapper(object):
    def __init__(self, service, operation):
        self.service = service
        self.operation = operation

    def __call__(self, packet, message, *args):
        return  self.service.callRPCMethod(self.operation, packet, message, *args)



