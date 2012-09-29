from bottle import route, run
import dropbox
import BaseHTTPServer
import cgi
import inspect
import urllib
import urlparse
import sys

from bottle import *
from Cookie import SimpleCookie
from dropbox import session, client

# XXX Fill in your consumer key and secret below
# You can find these at http://www.dropbox.com/developers/apps
APP_KEY = 'f4w2qalmhwpg2zf'
APP_SECRET = 'jvqpbo3po04ewue'
ACCESS_TYPE = 'app_folder' # should be 'dropbox' or 'app_folder' as configured for your app

HOST = None # override this if the server complains about missing Host headers
TOKEN_STORE = {}

def get_session():
    return session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)

def get_client(access_token):
    sess = get_session()
    sess.set_token(access_token.key, access_token.secret)
    return client.DropboxClient(sess)

class ExampleHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    @route('/index')
    def index_page():
        sess = get_session()
        request_token = sess.obtain_request_token()
        TOKEN_STORE[request_token.key] = request_token

        callback = "http://%s/callback" % (request.headers['host'])
        url = sess.build_authorize_url(request_token, oauth_callback=callback)
        prompt = """Click <a href="%s">here</a>"""
        return prompt % url

    @route('/callback')   
    def callback_page(self, oauth_token=None):
        # note: the OAuth spec calls it 'oauth_token', but it's
        # actually just a request_token_key...
        request_token_key = oauth_token
        if not request_token_key:
            return "Expected a request token key back!"

        sess = get_session()
        request_token = TOKEN_STORE[request_token_key]
        access_token = sess.obtain_access_token(request_token)
        TOKEN_STORE[access_token.key] = access_token

        self.set_cookie('access_token_key', access_token.key)
        return self.redirect('/index')    
    
run(host='localhost', port=8000, debug=True)