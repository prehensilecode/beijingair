#!/usr/bin/env python2.7
import cgi
import sys
import os
import webapp2
import datetime
#import json

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext.webapp import util

# modules to be included with this app
import twitter

debug_p = False
def datastore_create():
    #CREATE the datastore
    class tReading(db.Model):
        ckID = db.IntegerProperty(required=True)
        cFeedType = db.StringProperty(required=True,choices=set(["PM2","Ozone","PM2Avg","OzoneHigh"]))
        cDateTime = db.DateTimeProperty()
        cPM2p5Avg = db.FloatProperty()
        cOzoneHigh= db.IntegerProperty()
        cPM2p5_AQI_Quan = db.IntegerProperty()
        cPM2p5_AQI_Qual = db.StringProperty(required=False, choices=set(["Good","Moderate","Unhealthy for Sensitive Groups","Very Unhealthy","Hazardous"]))
        cOZONE_AQI_Quan = db.IntegerProperty()
        cOZONE_AQI_Qual = db.StringProperty(required=False, choices=set(["Good","Moderate","Unhealthy for Sensitive Groups","Very Unhealthy","Hazardous"]))

def aqi_definition(aqi):
    """Given an integer AQI, return the interpretation"""
    retval = ''
    if 0 <= aqi and aqi <= 50:
        retval = 'Good'
    elif 50 < aqi and aqi <= 100:
        retval = 'Moderate'
    elif 100 < aqi and aqi <= 150:
        retval = 'Unhealthy for Sensitive Groups'
    elif 150 < aqi and aqi <= 200:
        retval = 'Unhealthy'
    elif 200 < aqi and aqi <= 300:
        retval = 'Very Unhealthy'
    elif 300 < aqi and aqi <= 500:
        retval = 'Hazardous'
    else:
        retval = 'Out of Range'

    return retval
        

def crunch(data):
    concentration = []
    for x in data:
        #print("x['concentration'] = ", x['concentration'])
        if x['concentration'] >= 0.:
            # only print if there was data available (-ve number means no data)
            concentration.append(x['concentration'])

    data_max = max(concentration)
    data_min = min(concentration)
    data_mean = float(sum(concentration)) / len(concentration)
    
    return (data_max, data_min, data_mean)

def html_head():
    print '<html><head><title>Beijing Air Stats</title></head>'
    print '    <!--Load the AJAX API-->'
    print '    <script type="text/javascript" src="https://www.google.com/jsapi"></script>'
    print '    <script type="text/javascript">'
    
    print '      // Load the Visualization API and the piechart package.'
    print """      google.load('visualization', '1.0', {'packages':['corechart']});"""
      
    print '      // Set a callback to run when the Google Visualization API is loaded.'
    print '      google.setOnLoadCallback(drawChart);'
    
def html_data_table(pm, o3):
    # populate data table
    print '    </script'
    pass

def html_body(pm, o3, dt):
    print '<body>'
    print '<h4><a href="https://twitter.com/#!/BeijingAir">@BeijingAir</a> summary</h4>'

    (pm_max, pm_min, pm_mean) = crunch(pm)
    (o3_max, o3_min, o3_mean) = crunch(o3)

    print '<pre>'
    print 'Particulate matter (PM2.5) concentration (ppm):'
    print '    Mean: %.2f' % (pm_mean)
    print '    Max:  %.2f' % (pm_max)
    print '    Min:  %.2f' % (pm_min)
    print '</pre>'

    print ''
    print '<pre>'
    print 'Ozone concentration (ppm):'
    print '    Mean: %.2f' % (o3_mean)
    print '    Max:  %.2f' % (o3_max)
    print '    Min:  %.2f' % (o3_min)
    print '</pre>'

    print '<pre>No. of data points: pm - ', len(pm), '; o3 - ', len(o3), '</pre>'
    # stream is most recent first
    print '<pre>From: ', dt[-1], 'to', dt[0], '</pre>'

def html_tail():
    print '</body></html>'

def main():
    global debug_p
    t = twitter.api.Twitter(auth=twitter.oauth.OAuth('', '', '', ''))
    cur = t.statuses.user_timeline(screen_name="beijingair", include_rts=True)

    # There are 4 types of tweets: 
    # - instantaneous PM2.5 values
    # - instantaneous Ozone values
    # - 24-hr PM2.5 average
    # - 8-hr Ozone high
    # The instantaneous values for PM2.5 and Ozone do come at the same time, so
    # we can hash on datetime
    #
    # They look like, respectively:
    # - 03-04-2012 03:00; PM2.5; 113.0; 178; Unhealthy (at 24-hour exposure at this level)
    # - 03-03-2012 20:00; Ozone; 0.0; 0; Good (based on the higher of the current-hour and 8-hour readings)
    # - 03-03-2012 00:00 to 03-03-2012 23:59; PM2.5 24hr avg; 93.1; 167; Unhealthy
    # - 03-03-2012 00:00 to 03-03-2012 23:59;  Ozone 8hr high; 0.0; 0; Good
    # If there are no data, we get:
    # - 03-03-2012 14:00; PM2.5; no data

    pm = []
    o3 = []
    aqi = []
    dt = []
    j = []
    day = ''
    month = ''
    year = ''
    hr = ''
    mins = ''
    for s in cur:
        #print s['text']
        #print s['text'].split(';')
        #print s['text'].split(';')[0].split(' ')
        tweet = s['text'].split(';')
        #print 'tweet = ', tweet

        #print 'len(tweet) = ', len(tweet)
        datetime_field = tweet[0].split(' ')

        if len(tweet) > 3:
            # we only care about the instantaneous values
            if len(datetime_field) == 2:
                (d, t) = tweet[0].split(' ')
                (month, day, year) = d.split('-')
                (hr, mins) = t.split(':')
                dt.append(datetime.datetime(int(year), int(month), int(day), int(hr), int(mins)))
                if tweet[1].strip() == 'PM2.5':
                    pmraw = tweet[2]
                    aqiraw = tweet[3]
                    definitionraw = tweet[4]
                    pm.append({'concentration': float(pmraw.strip()), 'aqi': int(aqiraw.strip())})
                    if debug_p:
                        print 'date = ', d, '; time = ', t, '; pmraw = ', pmraw, '; aqiraw = ', \
                            aqiraw, '; definitionraw = ', definitionraw
                elif tweet[1].strip() == 'Ozone':
                    o3raw = tweet[2]
                    aqiraw = tweet[3]
                    definitionraw = tweet[4]
                    o3.append({'concentration': float(o3raw.strip()), 'aqi': int(aqiraw.strip())})
                    if debug_p:
                        print 'date = ', d, '; time = ', t, '; o3raw = ', o3raw, '; aqiraw = ', \
                            aqiraw, '; definitionraw = ', definitionraw
    
                aqiraw = tweet[3]
                definitionraw = tweet[4]


            # value for the entire "field" may be "no data" if there is no data 
            # available; e.g. 03-28-2011; 01:00; PM2.5; 40.0; 108; Unhealthy for Sensitive Groups // Ozone; no data
            # can tell from the length
            #if len(pmraw) == 1:
            #    #print('No PM data point')
            #    pm.append({'concentration': -1., 'aqi': -1, 'definition': 'n/a'})
            #else:
            #    pm.append({'concentration': float(pmraw[0]), 'aqi': int(pmraw[1]), 'definition': pmraw[2]})
    
            #if len(o3raw) == 1:
            #    #print('No O3 data point')
            #    o3.append({'concentration': -1., 'aqi': -1, 'definition': 'n/a'})
            #else:
            #    o3.append({'concentration': float(o3raw[0]), 'aqi': int(o3raw[1]), 'definition': o3raw[2]})
    
            #j.append(json.write(s)) 
    

    html_head()
    html_data_table(pm, o3)
    html_body(pm, o3, dt)

    html_tail()


    #for x in pm:
    #    print aqi_definition(x['aqi'])

    #for d in j:
    #    print '\n'.join([d.rstrip() for l in d.splitlines()])

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Hello, webapp World!')

app = webapp2.WSGIApplication([('/', MainPage)], 
                              debug=True)

