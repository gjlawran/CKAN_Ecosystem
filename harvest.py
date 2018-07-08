__author__ = 'gjlawran'
# an automated site survey of CKAN installations
# script visits each CKAN deployment and tries to determine the status, version, extensions and webserver
# script logs what it finds at each site and makes a summary of some observations


import requests
import json
import time
import logging
import os

logging.captureWarnings(True)


# create a directory using the current date
directory = './results/'+time.strftime("%Y%m%d")+'/'
try:
    if not os.path.exists(directory):
        os.makedirs(directory)
except IOError:
    print('Couldnt create or check directory', directory)

try:
    logfile = open(directory+'survey.log', 'w')
    logfile.write("Harvest start: " + time.strftime("%c")+"\n\n")

except IOError:
    print('Some sort of write error with the log file! ', logfile)

# use the OKF registry of CKAN instances as the list to harvest from
# TODO - expand to include those sites in dataportals
r = requests.get(
    'https://raw.githubusercontent.com/ckan/ckan-instances/gh-pages/config/instances.json')

data = r.json()

# TODO - remove after testing is complete
# data = data[0:9]  # remove after testing

# define dictionaries for collecting list of extensions, versions, OS
extCollection = {}
verCollection = {}
OSCollection = {}


# for each site determine status and store results to dictionaries

for i in range(0, len(data)):
    # compose and make status request for the site
    # TODO consider validating and parsing URL with urlparse module
    if data[i]['url']:
        URLinst = data[i]['url'].rstrip('//') + '/api/action/status_show'

    try:
        # TODO confirm handles both HTTP AND FORCED HTTPS
        m = requests.get(URLinst)

        # if possible determine the server type
        serverType = m.headers['server'] if 'server' in m.headers else 'unknown'

        # try and see if response header has correct type - note .get handles missing dict keys with a default
        if m.status_code == 200 and m.headers.get('content-type', 'missing') == 'application/json;charset=utf-8':

            # if we find a working machine print the  URL, status, and server type to console
            print(URLinst, m.status_code, serverType, " CKAN:",
                  m.json()['result']['ckan_version'])

            # log the siteURL, version, extensions
            writestring = URLinst + ', ' + serverType + \
                ", CKAN:" + m.json()['result']['ckan_version']
            logfile.write(writestring + ', ')
            json.dump(m.json()['result']['extensions'], logfile)
            logfile.write('\n')
            # store the version, server info and extensions into 3 dict
            verCollection.setdefault(
                m.json()['result']['ckan_version'], []).append(data[i]['url'])
            OSCollection.setdefault(serverType, []).append(data[i]['url'])

            # create a dictionary of the extensions used
            # key is extension, values are the URL of the site with extension
            for eachext in m.json()['result']['extensions']:
                extCollection.setdefault(eachext, []).append(data[i]['url'])

        else:   # output those sites that failed
            print("FAIL#"+URLinst, m.status_code, serverType)
            logfile.write(data[i]['url'] + ", #FAIL, " +
                          str(m.status_code) + "\n")

    except requests.exceptions.RequestException as e:
        print(e)


# serialize as JSON objects from dictionary collections and output  to files
def jsonObjective(dictname, dictlabel):
    values = [{dictlabel: k, "num": len(v), "sites": v}
              for k, v in dictname.items()]
    outjson = open(directory+dictlabel+'.json', 'w')
    json.dump(values, outjson, sort_keys=True)
    json.dump(values, logfile, sort_keys=True)
    outjson.close()


logfile.write('\n \n CKAN Version Deployments \n')
jsonObjective(verCollection, "VerName")

logfile.write('\n \n CKAN Extension Deployments \n')
jsonObjective(extCollection, "ExtName")

logfile.write('\n \n Web Server Information \n')
jsonObjective(OSCollection, "SiteInfo")


logfile.close()
