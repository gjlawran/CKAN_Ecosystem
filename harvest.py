__author__ = 'gjlawran'
# a script to harvest information on CKAN deployments

import requests
import json
import time

#output the results of the harvest to a text file
surveyed = open('surveyed.out','w')
surveyed.write("Current date & time " + time.strftime("%c")+"\n")
surveyed.write("Sites not responding to request:\n")

#use the OKF registry of CKAN instances as the list to harvest from
r = requests.get('http://instances.ckan.org/config/instances.json')
data = r.json()

#define dictionaries for collecting list of extensions, versions, OS
extCollection = {}
verCollection = {}
OSCollection = {}

# for each site determine status and store results to dicts

for i in range(1,len(data)):
    #compose and make status request for the site
    if data[i]['url'] : URLinst = data[i]['url'].rstrip('//') +'/api/action/status_show'
    try:
        m = requests.get(URLinst)

        # if possible determine the server type
        serverType = m.headers['server'] if 'server' in m.headers else 'unknown'

        # if we find a working machine print the  URL, status, and server type to console
        # also store the version, server info and extensions into 3 dict
        if m.status_code == 200 and m.headers['content-type'] == 'application/json;charset=utf-8':
            print URLinst, m.status_code, serverType," CKAN:", m.json()['result']['ckan_version']
            verCollection.setdefault(m.json()['result']['ckan_version'],[]).append(data[i]['url'])
            OSCollection.setdefault(serverType,[]).append(data[i]['url'])

            # create a dictionary of the extensions used
            # key is extension, values are the URL of the site with extension
            for eachext in m.json()['result']['extensions']:
                extCollection.setdefault(eachext,[]).append(data[i]['url'])

        else:   # output those sites that failed
            print "FAIL#"+URLinst, m.status_code, serverType
            surveyed.write( data[i]['url'] +" , "+ str(m.status_code) + "\n")

    except requests.exceptions.RequestException as e:
        print e


surveyed.write('\n')
json.dump(verCollection, surveyed)
surveyed.write( '\n \n')
json.dump(extCollection, surveyed)
surveyed.write( '\n \n')
json.dump(OSCollection, surveyed)

def sortOutDict(dictname):
    print (dictname)
    for keys in sorted(dictname):
        print len(dictname[keys]), keys, dictname[keys]
    print "\n"

sortOutDict(verCollection)
sortOutDict(OSCollection)
sortOutDict(extCollection)
