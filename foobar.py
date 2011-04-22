#!/usr/bin/env python2.5
from google.appengine.ext.webapp import util

import sys
import os

import datetime

#import simplejson as json
sys.path.insert(0, '.')
import json

#from twitter.api import Twitter
#from twitter.oauth import OAuth
#import twitter
sys.path.insert(0, 'twitter.zip')
import twitter


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
    print '<html><head><title>Beijing Air Stats</title></head><body>'

def html_tail():
    print '</body></html>'

def main():
    t = twitter.api.Twitter(auth=twitter.oauth.OAuth('', '', '', ''))
    
    cur = t.statuses.user_timeline(screen_name="beijingair", include_rts=True)
    
    pm = []
    o3 = []
    dt = []
    j = []
    day = ''
    month = ''
    year = ''
    hr = ''
    min = ''
    for s in cur:
        (d, t) = s['text'].split(';')[0:2]
        (month, day, year) = d.split('-')
        (hr, min) = t.split(':')
        dt.append(datetime.datetime(int(year), int(month), int(day), int(hr), int(min)))
        data = s['text'].split('//')
        pmraw = data[0].split(';')[3:]
        o3raw = data[1].split(';')[1:]
        #print 'date = ', date, '; time = ', time, '; pmraw = "', pmraw, '"; o3raw = "', o3raw, '"'

        # value for the entire "field" may be "no data" if there is no data 
        # available; e.g. 03-28-2011; 01:00; PM2.5; 40.0; 108; Unhealthy for Sensitive Groups // Ozone; no data
        # can tell from the length
        if len(pmraw) == 1:
            #print('No PM data point')
            pm.append({'concentration': -1., 'aqi': -1, 'definition': 'n/a'})
        else:
            pm.append({'concentration': float(pmraw[0]), 'aqi': int(pmraw[1]), 'definition': pmraw[2]})

        if len(o3raw) == 1:
            #print('No O3 data point')
            o3.append({'concentration': -1., 'aqi': -1, 'definition': 'n/a'})
        else:
            o3.append({'concentration': float(o3raw[0]), 'aqi': int(o3raw[1]), 'definition': o3raw[2]})

        j.append(json.write(s))

    
    (pm_max, pm_min, pm_mean) = crunch(pm)
    (o3_max, o3_min, o3_mean) = crunch(o3)

    html_head()

    print '<pre>'
    print 'Particulate matter concentration (ppm):'
    print '    Mean: ', pm_mean
    print '    Max:  ', pm_max
    print '    Min:  ', pm_min
    print '</pre>'

    print ''
    print '<pre>'
    print 'Ozone concentration (ppm):'
    print '    Mean: ', o3_mean
    print '    Max:  ', o3_max
    print '    Min:  ', o3_min
    print '</pre>'

    print '<pre>No. of data points: pm - ', len(pm), '; o3 - ', len(o3), '</pre>'
    # stream is most recent first
    print '<pre>From: ', dt[-1], 'to', dt[0], '</pre>'

    html_tail()


    #for x in pm:
    #    print aqi_definition(x['aqi'])

    #for d in j:
    #    print '\n'.join([d.rstrip() for l in d.splitlines()])


if __name__ == '__main__':
    main()
