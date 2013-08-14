import webapp2
import cgi
from webapp2_extras import json
from google.appengine.api import urlfetch
import aws_utils

class TestHandler(webapp2.RequestHandler):

    def get(self):
        #command = cgi.escape(self.request.get('command'))
        #command.replace(' ', '')
        #if len(command) == 0:
        #    response = {'status': 'ERROR'}
        #    self.response.headers['Content-Type'] = 'application/json'
        #    self.response.set_status(400)
        #    self.response.out.write(json.encode(response))
        #    return

        # Get the closest region.
        lati_longi = self.request.headers['X-AppEngine-CityLatLong']
        lati, longi = lati_longi.split(',')
        region = aws_utils.closest_region(float(lati), float(longi))

        # Count the number of instances.
        running = aws_utils.count_instances(region, 'running')
        pending = aws_utils.count_instances(region, 'pending')

        if running == 0 and pending == 0:
            # Create an instance.
            aws_utils.create_an_instance(region)

            # Return the response.
            response = {'status': 'STARTING'}
            self.response.headers['Content-Type'] = 'application/json'
            self.response.set_status(200)
            self.response.out.write(json.encode(response))
            return

        elif running == 0 and pending != 0:
            # Still waiting for the instance to boot up.

            # Return the response.
            response = {'status': 'PENDING'}
            self.response.headers['Content-Type'] = 'application/json'
            self.response.set_status(200)
            self.response.out.write(json.encode(response))
            return

        # We assume that we have a running instance in the region.

        instance_dns = aws_utils.get_an_instance_dns(region)
        url = 'http://%s:8080/info' % (instance_dns)

        result = urlfetch.fetch(url=url)
        
        # Return the response.
        response = {}
        response['status'] = 'OK'
        response['region'] = region['city']
        response['result'] = result.content
        self.response.headers['Content-Type'] = 'application/json'
        self.response.set_status(200)
        self.response.out.write(json.encode(response))
