__author__ = 'kivsiak@gmail.com'

import web


urls = (
    '/', 'index'
    )

class index:
    def GET(self):
        web.header('Content-Type', 'text/html')
        return "aaa"

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.internalerror = web.debugerror
    app.run()
