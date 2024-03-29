import cgi
import os
import sys
import datetime
import json
import webapp2
import httplib2
import oauth2

#sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
#sys.path.insert(0, 'twitter.zip')
#from twitter.api import Twitter
#from twitter.oauth import OAuth

from google.appengine.ext.webapp import template

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

class Greeting(db.Model):
    author = db.UserProperty()
    content = db.StringProperty(multiline=True)
    date = db.DateTimeProperty(auto_now_add=True)

class MainPage(webapp2.RequestHandler):
    def get(self):
        greetings_query = Greeting.all().order('-date')
        greetings = greetings_query.fetch(10)

        user = users.get_current_user()

        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
                           'greetings': greetings,
                           'url': url,
                           'url_linktext': url_linktext,
                          }

        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))

class Guestbook(webapp2.RequestHandler):
    def post(self):
        greeting = Greeting()

        if users.get_current_user():
            greeting.author = users.get_current_user()

        greeting.content = self.request.get('content')
        greeting.put()
        self.redirect('/')

app = webapp2.WSGIApplication(
                              [('/', MainPage),
                               ('/sign', Guestbook)],
                              debug=True)

