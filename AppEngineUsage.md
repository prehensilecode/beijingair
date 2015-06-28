# App Engine #
## Command Line Usage ##
  * Assume that the code is in `~/Projects/beijingair`
  * To run the code on a local instance of the AppEngine:
```
       cd Projects
       dev_appserver.py beijingair/
```
  * Then, in a web browser, enter `http://localhost:8080`
  * Once you're satisfied, you can upload the app to the AppEngine host
```
       appcfg.py update beijingair/
       [many messages]
```
  * appcfg.py wants your regular @gmail.com email address and password
  * Once the update is done, check the hosted site: `http://beijingairstats-hrd.appspot.com/`

## IDE Usage ##
  * Or, you can try to develop and run with the Eclipse IDE:
> > http://googlewebtoolkit.blogspot.com/2011/03/top-ten-reasons-to-use-google-plugin.html