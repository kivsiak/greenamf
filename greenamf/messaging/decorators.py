# -*- coding: utf-8 -*-
__author__ = 'kivsiak@gmail.com'


def operation(name, auth = False):
    def realDecorator(f):
        f.name = name
        f.auth = False
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

def input(*requireds, **defaults):
    """
    Returns a `storage` object with the GET and POST arguments.
    See `storify` for how `requireds` and `defaults` work.
    """
    _method = defaults.pop('_method', 'both')
    pass

ctx = Context()





class RPCServiceBase(type):
    def __new__(cls, name, bases, attrs):
        super_new = super(RPCServiceBase, cls).__new__
        parents = [b for b in bases if isinstance(b, RPCServiceBase)]
        if not parents:
            # If this isn't a subclass of Model, don't do anything special.
            return super_new(cls, name, bases, attrs)
        attrs['operations'] = {}
        for key, attr in attrs.items():
            if hasattr(attr, '__call__') and attr.operation:
                attrs['operations'][attr.name] = attr
                def methodError(self):
                    raise NotImplementedError("%s cannot be called directly" % key)
                attrs[key] = methodError
        return super_new(cls, name, bases, attrs)

def mine(self):
        pass

class RPCService(object):
    __metaclass__ = RPCServiceBase

    def __init__(self):

        super(RPCService, self).__init__()
        for name, operation in self.operations.items():
            # тут типа меппить операции на сервис используя стандартные средства amfast
            pass



class Context(object):
    pass

@Service('myService')
class MyService(RPCService):

    @operation("true")
    def operationA(self):
        input()
        return True

    @operation("echo")
    def operationB(self, arg):
        ctx.get()
        return arg



service = MyService()
service.operationA()
pass

