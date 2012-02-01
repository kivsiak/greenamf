__author__ = 'kivsiak@gmail.com'


class A(object):
    def __init__(self, app):
        print "a"
        self.app  = app

class B(object):
    def __init__(self, app):
        print "b"
        self.app = app


class C(object):
    def __init__(self, app, args):
        print "C " + args
        self.args = args
        self.app =app

class APP(object):
    def __init__(self):
        print "aapp"


chain = [A, B, (C, "args")]


d = A(B(C( APP(), "args")))
#chain.reverse()
result = APP()
for item in chain:
    if type(item) == tuple:
        result = item[0](result, *item[1:])
    else:
        result = item(result)

print d

print result