import webapp2
import cgi
from webapp2_extras import json
from google.appengine.api import urlfetch
import aws_utils

class StatusHandler(webapp2.RequestHandler):

    def get(self):
        #command = cgi.escape(self.request.get('command'))
        #command.replace(' ', '')
        #if len(command) == 0:
        #    response = {'status': 'ERROR'}
        #    self.response.headers['Content-Type'] = 'application/json'
        #    self.response.set_status(400)
        #    self.response.out.write(json.encode(response))
        #    return

        # Return the response.
        response = {}
        response['status'] = 'OK'
        response['result'] = aws_utils.get_status()
        self.response.headers['Content-Type'] = 'application/json'
        self.response.set_status(200)
        self.response.out.write(json.encode(response))
