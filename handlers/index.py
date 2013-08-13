import webapp2

class IndexHandler(webapp2.RequestHandler):

    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('http://github.com/donny/mako-mori')
