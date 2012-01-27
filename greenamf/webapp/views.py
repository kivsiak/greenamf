import gevent
import web

__author__ = 'kivsiak@gmail.com'


class Index():
    def GET(self):
        render = web.template.render('templates/')
        return render.base()

class LongPull:
    def GET(self):
        return "Hello, world! long"
    def POST(self):
        web.header('Content-Type', 'text/plain')
        gevent.sleep(10)
        return "Hello, world! long"


class Pull:
    def GET(self):
        return "Hello, world!"
    def POST(self):
        web.header('Content-Type', 'application/x-www-form-urlencoded');
        return "Hello, world! "
