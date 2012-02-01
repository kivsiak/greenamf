import argparse
from gevent.pool import Pool
from gevent.pywsgi import WSGIServer
from greenamf.Node import Node
from thc import settings

__author__ = 'kivsiak@gmail.com'

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='ArgPasser.')
    parser.add_argument("-p", "--port", type=int, default=80, dest='port', help="listener port")
    parser.add_argument("-b", "--bind", type=str, default=None, help="bind address")
    parser.add_argument("-D", "--remoteDebug", action="store_true", help="enable remote debug")
    args = parser.parse_args()
    print 'Serving on...' + str(args.port)
    pool = Pool(10000)
    WSGIServer(('', args.port), Node(settings.settings).getHandler(), spawn=pool).serve_forever()