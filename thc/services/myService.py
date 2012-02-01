from amfast.remoting.channel import SecurityError
import gevent

__author__ = 'kivsiak@gmail.com'

from greenamf.messaging.decorators import operation, RPCService, Service

@Service('myService')
class MyService(RPCService):

    @operation("returnTrue", secure=True)
    def operationA(self):
        return True

    @operation("echo", secure=True)
    def operationB(self, arg):
        print "aaa"
        return arg


@Service('authService')
class AuthService(RPCService):

    @operation(name="login")
    def login(self):
        try:
            user_id = self.app.web_context.env['beaker.session']['user_id']
        except KeyError:
            pass
            #raise SecurityError('Authentication not implemented.')
        command = self.context.msg.body[0]
        command.connection.authenticate('user_id')
        return  True

    @operation(name="logout")
    def logout(self):
        pass

    @operation()
    def pushUser(self, user):
        pass
