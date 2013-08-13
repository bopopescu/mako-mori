import webapp2
from webapp2_extras import json
from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.api import urlfetch

class TestHandler(webapp2.RequestHandler):

	def get(self):

		# Log the request.
		ip_address = self.request.remote_addr
		lat_long = self.request.headers['X-AppEngine-CityLatLong']

		# Return the response.
		self.response.headers['Content-Type'] = 'application/json'
		self.response.set_status(200)
		self.response.out.write("{\"result\": \"OK %s\"}\n" % (lat_long))
