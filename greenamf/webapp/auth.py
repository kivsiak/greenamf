# -*- coding: utf-8 -*-
from werkzeug.wrappers import Request, Response

__author__ = 'kivsiak@gmail.com'


class AuthManager(object):
    pass



class AuthRequest(Request):
    def __init__(self, environ, populate_request=True, shallow=False):
        super(AuthRequest, self).__init__(environ, populate_request, shallow)

    @property
    def user(self):
        try:
            userId = self.session['userId']
            return  userId
        except KeyError:
            return  None

    @property
    def session(self):
        try:
            return self.environ['beaker.session']
        except  KeyError as e:
            raise  KeyError(e, "Session is not intitialized")


def auth_required(func):
    def wrapper(request, *args, **kvargs):
        if not request.user:
            return  Response("Auth required", status=503)
        return  func(request, *args, **kvargs)

    return  wrapper