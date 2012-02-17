__author__ = 'kivsiak@gmail.com'

class StripPathMiddleware(object):
    def __init__(self, app):
        self.app = app


    def __call__(self, e, h):
        e['PATH_INFO'] = e['PATH_INFO'].rstrip('/')
        return self.app(e, h)

