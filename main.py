import os, sys, config

# Force sys.path to have our own directory first, so we can import from it.
sys.path.insert(0, config.APP_ROOT_DIR)
sys.path.insert(1, os.path.join(config.APP_ROOT_DIR, 'external'))

import webapp2
from handlers import index, test

app = webapp2.WSGIApplication([
								('/', index.IndexHandler),
								('/test', test.TestHandler)
								], debug=True)
