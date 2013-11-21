#!/usr/bin/python
# Copyright 2013 Julien Henry
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from gpxpy import gpxpy
import simplejson
import urllib
import sys
from optparse import OptionParser

def usage():
    print "Usage : python addelevation.py <filename>.gpx"

parser = OptionParser()
parser.add_option("-o", "--output", dest="outputfile", default="output.gpx",
                  help="name of the output file", metavar="FILE")
parser.add_option("-v", "--verbose",
                  action="store_false", dest="verbose", default=False,
                  help="verbose mode")

(options, args) = parser.parse_args()

if len(args) == 1 :
    filename = args[0]
else:
    print "wrong or missing arguments"
    usage()
    sys.exit(1)

outputfile=options.outputfile

try:
    gpx_file = open(filename, 'r')
except:
    print filename + " is not a valid gpx file\n"
    sys.exit(1)

ELEVATION_BASE_URL = 'http://maps.googleapis.com/maps/api/elevation/json'

def getElevation(locations,sensor="false", **elvtn_args):
    elvtn_args.update({
        'locations': locations,
        'sensor': sensor
        })

    url = ELEVATION_BASE_URL + '?' + urllib.urlencode(elvtn_args)
    if options.verbose:
        print url
    response = simplejson.load(urllib.urlopen(url))

    # Create a dictionary for each results[] object
    elevationArray = []

    for resultset in response['results']:
        elevationArray.append(resultset['elevation'])

    return elevationArray

gpx = gpxpy.parse(gpx_file)
locationsArray = []

for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            if options.verbose:
                print 'Point at ({0},{1}) -> {2}'.format(point.latitude, point.longitude, point.elevation)
            locationsArray.append('{0},{1}'.format(point.latitude,point.longitude))

for waypoint in gpx.waypoints:
    if options.verbose:
        print 'waypoint {0} -> ({1},{2})'.format(waypoint.name, waypoint.latitude, waypoint.longitude)

for route in gpx.routes:
    if options.verbose:
        print 'Route:'
    for point in route:
        if options.verbose:
            print 'Point at ({0},{1}) -> {2}'.format(point.latitude, point.longitude, point.elevation)

locs = ""
size=0
elevationArray = []
for loc in locationsArray:
    if size == 0 :
        locs = loc
    else:
        locs = locs + '|' + loc
    size = size+1
    # limit the size of the arguments to 50, otherwise the query to the Google
    # API fails
    # 50 has been chosen, since the queries seem to always work with this
    # parameter
    if size > 50 :
        elevationArray = elevationArray + getElevation(locs)
        size = 0
elevationArray = elevationArray + getElevation(locs)

i = 0
for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            point.elevation=elevationArray[i]
            i=i+1

f = open(outputfile, 'w')
f.write(gpx.to_xml())
f.close()

print "finished... Resulting GPX stored in " + outputfile
