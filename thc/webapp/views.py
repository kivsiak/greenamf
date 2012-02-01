import gevent
from werkzeug.wrappers import Response
from thc.domain.models import User

__author__ = 'kivsiak@gmail.com'


def index(request):
    db = request.app.session
    user = db.query(User).first()
    return  Response("Index")

def longPull(request):
        def pull():
            yield "starting"
            gevent.sleep(2)
            yield "1"
            gevent.sleep(2)
            yield "2"
            gevent.sleep(2)
            yield "3"
            gevent.sleep(2)
            yield "4"
        return  Response(pull(), direct_passthrough = True)


def pull(request):
    request.session['user_id'] = "aaa"
    return  Response("Hello, world! long")
