#!/usr/bin/env python2.7
import logging
import cgi
import sys
import os
import re
import webapp2
import datetime
import wsgiref.handlers
#import json

from google.appengine.ext import db
from google.appengine.ext.webapp import util

# modules to be included with this app
#import twitter

sys.path.insert(0, 'oauth2.zip')
sys.path.insert(0, 'httplib2.zip')
sys.path.insert(0, 'tweepy.zip')

import oauth2
import httplib2
import tweepy

# XXX keys.txt to be inserted here

debug_p = False

#def datastore_create():
#    #CREATE the datastore
#    class tReading(db.Model):
#        ckID = db.IntegerProperty(required=True)
#        cFeedType = db.StringProperty(required=True,choices=set(["PM2","Ozone","PM2Avg","OzoneHigh"]))
#        cDateTime = db.DateTimeProperty()
#        cPM2p5Avg = db.FloatProperty()
#        cOzoneHigh= db.IntegerProperty()
#        cPM2p5_AQI_Quan = db.IntegerProperty()
#        cPM2p5_AQI_Qual = db.StringProperty(required=False, choices=set(["Good","Moderate","Unhealthy for Sensitive Groups","Very Unhealthy","Hazardous"]))
#        cOZONE_AQI_Quan = db.IntegerProperty()
#        cOZONE_AQI_Qual = db.StringProperty(required=False, choices=set(["Good","Moderate","Unhealthy for Sensitive Groups","Very Unhealthy","Hazardous"]))

class Reading(db.Model):
    """Models an individual air quality reading of PM2.5 and O3 at a certain datetime"""
    dt    = db.DateTimeProperty(auto_now_add=False)
    pm    = db.FloatProperty()
    pmaqi = db.IntegerProperty()
    o3    = db.FloatProperty()
    o3aqi = db.IntegerProperty()

# We'll only ever have one instance of the Beijingair
def beijingair_key(beijingair_name=None):
    """Constructs a datastore key for a Beijingair entity with beijingair_name."""
    return db.Key.from_path('Beijingair', 'default_beijingair')

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
    if (len(data) > 0):
        concentration = []
        for x in data:
            #print("x['concentration'] = ", x['concentration'])
            if x['concentration'] >= 0.:
                # only print if there was data available (-ve number means no data)
                concentration.append(x['concentration'])

        data_max = max(concentration)
        data_min = min(concentration)
        data_mean = float(sum(concentration)) / len(concentration)
    else:
        data_max = -1
        data_min = -1
        data_mean = -1

    return (data_max, data_min, data_mean)

def dummy_head():
    s = """<html><head><title>Beijing Air Stats</title></head>"""
    return s

def dummy_body():
    s = """
        <body>
            <h1>hello, world</h1>
        </body>
        </html>"""
    return s


class MainPage(webapp2.RequestHandler):
    def get(self):
        self.main()
        self.response.out.write(self.html_head(self.dt, self.pm, self.o3))
        self.response.out.write(self.html_data_table(self.dt, self.pm, self.o3))
        self.response.out.write(self.html_body(self.dt, self.pm, self.o3))
        self.response.out.write(self.html_tail())

    def html_head(self, dt, pm, o3):
        s = """<html><head><title>Beijing Air Stats</title></head>
            <!--Load the AJAX API-->
            <script type="text/javascript" src="https://www.google.com/jsapi"></script>
            <script type="text/javascript">
                // Load the Visualization API and the piechart package.
                google.load('visualization', '1.0', {'packages':['corechart']});
                // Set a callback to run when the Google Visualization API is loaded.
                google.setOnLoadCallback(drawChart);
            """
        return s

    def html_data_table(self, dt, pm, o3):
        retstr = ''
        # populate data table
        if (len(pm) > 0 and len(o3) > 0):
            datatable_strings = ["""    function drawChart() {
                         var pm_data = new google.visualization.DataTable();
                         var o3_data = new google.visualization.DataTable();
                         pm_data.addColumn('datetime', 'Date/Time (local)');
                         pm_data.addColumn('number', 'PM2.5 (ppm)');
                         pm_data.addRows(["""]
            for i in range(len(pm)):
                datatable_strings.append("              [new Date(%d, %d, %d, %d, %d, %d), %f]," % (dt[i].year, dt[i].month, dt[i].day, dt[i].hour, dt[i].minute, dt[i].second, pm[i]['concentration']))

            datatable_strings.append("""          ]);
                  o3_data.addColumn('datetime', 'Date/Time (local)');
                  o3_data.addColumn('number', 'O3 (ppm)');
                  o3_data.addRows([""")

            for i in range(len(o3)):
                datatable_strings.append("              [new Date(%d, %d, %d, %d, %d, %d), %f]," % (dt[i].year, dt[i].month, dt[i].day, dt[i].hour, dt[i].minute, dt[i].second, o3[i]['concentration']))

            datatable_strings.append("""          ]);
                  var pm_options = { title: 'Beijing Air Quality: PM2.5 (ppm)', vAxis: {logScale: false}};
                  var o3_options = { title: 'Beijing Air Quality: O3 (ppm)', vAxis: {logScale: false}};
                  var pm_chart = new google.visualization.LineChart(document.getElementById('pm_chart_div'));
                  var o3_chart = new google.visualization.LineChart(document.getElementById('o3_chart_div'));
                  pm_chart.draw(pm_data, pm_options);
                  o3_chart.draw(o3_data, o3_options);
              }
            </script>""")
            retstr = ''.join(datatable_strings)
        elif (len(pm) > 0 and len(o3) == 0):
            datatable_strings = ["""    function drawChart() {
                         var pm_data = new google.visualization.DataTable();
                         pm_data.addColumn('datetime', 'Date/Time (local)');
                         pm_data.addColumn('number', 'PM2.5 (ppm)');
                         pm_data.addRows(["""]
            for i in range(len(pm)):
                datatable_strings.append("              [new Date(%d, %d, %d, %d, %d, %d), %f]," % (dt[i].year, dt[i].month, dt[i].day, dt[i].hour, dt[i].minute, dt[i].second, pm[i]['concentration']))

            datatable_strings.append("""          ]);
                  var pm_options = { title: 'Beijing Air Quality: PM2.5 (ppm)', vAxis: {logScale: false}};
                  var pm_chart = new google.visualization.LineChart(document.getElementById('pm_chart_div'));
                  pm_chart.draw(pm_data, pm_options);
              }
            </script>""")
            retstr = ''.join(datatable_strings)
        elif (len(pm) == 0 and len(o3) > 0):
            datatable_strings = ["""    function drawChart() {
                         var o3_data = new google.visualization.DataTable();
                         o3_data.addColumn('datetime', 'Date/Time (local)');
                         o3_data.addColumn('number', 'O3 (ppm)');
                         o3_data.addRows(["""]

            for i in range(len(o3)):
                datatable_strings.append("              [new Date(%d, %d, %d, %d, %d, %d), %f]," % (dt[i].year, dt[i].month, dt[i].day, dt[i].hour, dt[i].minute, dt[i].second, o3[i]['concentration']))

            datatable_strings.append("""          ]); 
                var o3_options = { title: 'Beijing Air Quality: O3 (ppm)', vAxis: {logScale: false}};
                var o3_chart = new google.visualization.LineChart(document.getElementById('o3_chart_div'));
                  o3_chart.draw(o3_data, o3_options);
                  }
            </script>""")
            retstr = ''.join(datatable_strings)
        else:
            retstr = '</script>'

        return retstr

    def html_body(self, dt, pm, o3):
        (pm_max, pm_min, pm_mean) = crunch(pm)
        (o3_max, o3_min, o3_mean) = crunch(o3)

        bodyhead_str = """<body>
            <h2><a href="https://twitter.com/#!/BeijingAir">@BeijingAir</a> Summary</h2>"""

        body_strings = []
        if (len(pm) > 0 and len(o3) > 0):
            body_strings =  ["""
            <div id="pm_chart_div" style="width: 900px; height: 500px;"></div>\n
            <p>&nbsp;</p>\n
            <div id="o3_chart_div" style="width: 900px; height: 500px;"></div>\n"""]
        elif (len(pm) > 0 and len(o3) == 0):
            body_strings =  ["""
            <div id="pm_chart_div" style="width: 900px; height: 500px;"></div>\n"""]
        elif (len(pm) == 0 and len(o3) > 0):
            body_strings =  ["""
            <div id="o3_chart_div" style="width: 900px; height: 500px;"></div>\n"""]
        
        if (len(pm) > 0 or len(o3) > 0):
            body_strings.append(" <h4>Summary statistics</h4>\n<pre>")

        if (len(pm) > 0):
            body_strings.append('    Particulate matter (PM2.5) concentration (ppm):\n')
            body_strings.append('         Mean: %7.2f\n' % (pm_mean))
            body_strings.append('         Max:  %7.2f\n' % (pm_max))
            body_strings.append('         Min:  %7.2f\n\n' % (pm_min))

        if (len(o3) > 0):
            body_strings.append("""    Ozone concentration (ppm):\n""")
            body_strings.append('         Mean: %7.2f\n' % (o3_mean))
            body_strings.append('         Max:  %7.2f\n' % (o3_max))
            body_strings.append('         Min:  %7.2f\n\n' % (o3_min))

        body_strings.append('    No. of data points: pm - %d, o3 - %d\n' % (len(pm), len(o3)))
        # stream is most recent first
        body_strings.append('    From: %s to %s</pre>' % (dt[-1], dt[0]))

        if (len(pm) > 0 or len(o3) > 0):
            body_strings.append("</pre>")

        #print '<pre>dt = ', dt
        #print 'pm = ', pm
        #print 'o3 = ', o3
        #print '</pre>'

        return ''.join([bodyhead_str, ''.join(body_strings)])

    def html_tail(self):
        return '</body></html>'

    def main(self):
        global debug_p
        ### verdone
        #t = twitter.api.Twitter(auth=twitter.oauth.OAuth('', '', '', ''))
        #cur = t.statuses.user_timeline(screen_name="beijingair", include_rts=True)

        ### other python-twitter
        #t = twitter.Api(consumer_key="w2eecV8eFoAnHFpr4buJA", consumer_secret="y96hd3WmBiWequGLLtgwVq3zPzNlbmx4gdzLADZIs", access_token_key="9114072-HF350O2gvAyaXsyzgZexBn1xKUPCn46iND91xMrrVs", access_token_secret="MLlgwrTIsMPFJh7WqHud5nSZfuR7vyAHHm8pP7InXk", cache=None)
        #cur = t.statuses.user_timeline(screen_name="beijingair", include_rts=True)

        ### tweepy
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)
        #bj = api.get_user(screen_name='beijingair')
        cur = api.user_timeline(screen_name="beijingair", include_rts=True)
        

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
        # - 03-03-2012 12:00 to 03-03-2012 11:59; PM2.5 24hr avg; 93.1; 167; Unhealthy
        # - 03-03-2012 12:00 to 03-03-2012 11:59;  Ozone 8hr high; 0.0; 0; Good
        # If there are no data, we get:
        # - 03-03-2012 14:00; PM2.5; no data

        # pattern which matches the date-time part of the 24-hr period average tweet.
        avgpat = re.compile(r'^\d{2}-\d{2}-\d{4}\ \d{2}:\d{2}\ to\ \d{2}-\d{2}-\d{4}\ \d{2}:\d{2}')

        self.pm = []
        self.o3 = []
        aqi = []
        self.dt = []
        j = []
        day = ''
        month = ''
        year = ''
        hr = ''
        mins = ''
        q = Reading.all(keys_only=True)
        for s in cur:
            if len(s.text) > 3:
                if not avgpat.match(s.text):
                    datetime_field = s.text.split(';')[0]
                    reading = s.text.split(';')[1:]
                    # we only care about the instantaneous values
                    pmraw = -1.
                    o3raw = -1.
                    pmaqiraw = 0
                    o3aqiraw = 0
                    if len(datetime_field) > 0:
                        (d, t) = datetime_field.split(' ')
                        (month, day, year) = d.split('-')
                        (hr, mins) = t.split(':')
                        cur_dt = datetime.datetime(int(year), int(month), int(day), int(hr), int(mins))
                        self.dt.append(cur_dt)
                        if reading[0].strip() == 'PM2.5':
                            if reading[1].strip() != 'No Reading':
                                pmraw = float(reading[1].strip())
                                pmaqiraw = int(reading[2].strip())
                                definitionraw = reading[3].strip()
                                self.pm.append({'concentration': pmraw, 'aqi': pmaqiraw})
                                if debug_p:
                                    print 'date = ', d, '; time = ', t, '; pmraw = ', pmraw, '; aqiraw = ', \
                                        aqiraw, '; definitionraw = ', definitionraw
                        elif reading[0].strip() == 'Ozone':
                            if reading[1].strip() != 'No Reading':
                                o3raw = float(reading[1].strip())
                                o3aqiraw = int(reading[2].strip())
                                definitionraw = reading[3].strip()
                                self.o3.append({'concentration': o3raw, 'aqi': o3aqiraw})
                                if debug_p:
                                    print 'date = ', d, '; time = ', t, '; o3raw = ', o3raw, '; aqiraw = ', \
                                        aqiraw, '; definitionraw = ', definitionraw

                        key_name = ' '.join(['reading', str(cur_dt)])
                        q.filter("key_name =", key_name)
                        result = q.get()
                        if not result:
                            r_data = Reading(key_name=key_name, dt=cur_dt, pm=pmraw, pmaqi=pmaqiraw, o3=o3raw, o3aqi=o3aqiraw)
                            r_data.put()
    
    
    

class Beijingair(webapp2.RequestHandler):
    def post(self):
        beijingair_name = 'default_beijingair'
        reading = Reading(parent=beijingair_key(beijingair_name))


app = webapp2.WSGIApplication([('/', MainPage)],
                              debug=True)

