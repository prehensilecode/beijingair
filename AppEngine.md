# App Engine #
App Engine is Google's web application framework:
> http://code.google.com/appengine/

We use the Python version.

# Python #
App Engine uses a modified Python 2.5. Besides the version, there is the issue of how to include other Python modules.

## Importing Modules ##
  * Modules can be uploaded together with the application code
  * For small single or few-file modules, they can be uploaded directly into a subdirectory
    * Example: we use a json module that's in a single file json.py in the beijingair directory
```
         sys.path.insert(0, '.')
         import json
```
  * For large modules, it is better to zip the module files up into a single file, and use the zipimport module (included in App Engine) to load modules
  * Example: We use [Python Twitter Tools (PTT) 1.4.2](http://mike.verdone.ca/twitter/) -- we may update to 1.5.2 at some point.
    * To create the zip file:
```
        cd ~/Projects/beijingair
        wget http://mike.verdone.ca/twitter/dist/twitter-1.4.2.tar.gz
        tar zxf twitter-1.4.2.tar.gz
        mv twitter-1.4.2/twitter .
        rm -rf twitter-1.4.2
        zip -r twitter.zip twitter/
          adding: twitter/ (stored 0%)
          adding: twitter/twitter_globals.py (deflated 55%)
          adding: twitter/api.py (deflated 66%)
          adding: twitter/__init__.py (deflated 32%)
          adding: twitter/oauth_dance.py (deflated 62%)
          adding: twitter/cmdline.py (deflated 71%)
          adding: twitter/oauth.py (deflated 62%)
          adding: twitter/util.py (deflated 37%)
          adding: twitter/ansi.py (deflated 59%)
          adding: twitter/ircbot.py (deflated 68%)
          adding: twitter/auth.py (deflated 59%)
```
  * Then, the zip file must be added to the import path. In the main Python script for the application, do:
```
        sys.path.insert(0, 'twitter.zip')
        import twitter
```