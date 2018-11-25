'''
--- Content Delivery Network ---
Measures delays
Finds Shortest path between nodes
Handles the requests
Caches the responses
Logs the files..

------------------------
Author: Ibrahim Mohammad
 University of Houston
------------------------
'''


from http.server import HTTPServer, BaseHTTPRequestHandler
import http.client
from socketserver import ThreadingMixIn
import threading
import os.path
import time
import datetime
import json
import urllib.request
import urllib.parse
import sys
import random
import mimetypes
SERVER_IP = ''
PROXY_PORT = int(sys.argv[1])
CONFIG_FILE = sys.argv[2]
HEART_BEATS = True
HEART_BEAT_TIMEOUT = 600
CACHE_TIMEOUT = 100 #Cache file Delete timeout
CACHE_TYPE_ONE = 'type1'
CACHE_TYPE_TWO = 'type2'
CACHE_NEED_HEADER = 'isCacheNeeded' #Used in header to know if the file needs to be cached or not in response

# Returns Config file contents
def getConfigFile():
    contents =''
    f = open(CONFIG_FILE, 'r')
    contents = f.read()
    f.close()
    config = json.loads(contents)
    return config

#Returns Neighbors of this node as a list
def getNeighbors():
    config = getConfigFile()
    links = config["links"]
    numLinks = len(links)
    l = []
    for i in range(numLinks):
        l.append([links[i]['geo_tag'], links[i]['node_ip'], links[i]['node_port'], links[i]['link_delay']])
    return l

# Initial routing table
def createRoutingTable(updatedNeighbors):
    config = getConfigFile()
    myNodeIp = config['node_ip']
    myNodePort = config['node_port']
    myGeoTag = config['geo_tag']
    rTable = {}
    rTable[myGeoTag] = [[myNodeIp, myNodePort], '0', [myGeoTag, [myNodeIp, myNodePort]]]
    for i in updatedNeighbors:
        rTable[i[0]] = [[i[1], i[2]], i[3], [i[0], [i[1], i[2]]]]
    fileName = 'RT_' + getConfigFile()["node_name"] + '.txt'
    f = open(fileName, "w+")
    f.write(str(rTable))
    f.close()
    return True
# Creating initial routing table using neighbors information, delays will be updated later.
createRoutingTable(getNeighbors())

#Creating Log file based on the filename provided in config file
def createLogFile():
    fileName = getConfigFile()['log_file']
    f = open(fileName, "w+")
    f.close()
createLogFile()

def updateLogFile(data):
    fileName = getConfigFile()['log_file']
    f = open(fileName, "a+")
    lst = str(datetime.datetime.now())+'\n' + data +'\n'
    f.write(lst)
    f.close()

#Updates routing table with updated routes added as input.
def updateRoutingTable(rt):
    fileName = 'RT_' + getConfigFile()["node_name"] + '.txt'
    f = open(fileName, "w+")
    f.write(str(rt))
    f.close()
def readRoutingTable():
    fileName = 'RT_' + getConfigFile()["node_name"] + '.txt'
    f = open(fileName, "r")
    contents = f.read()
    f.close()
    return eval(contents)
def readUpdatedRoutingTable():
    fileName = 'RT_' + getConfigFile()["node_name"] + '.txt'
    f = open(fileName, "r")
    contents = f.read()
    f.close()
    return eval(contents)

#Sending this node IP, PORT, GEO_TAG details taken from config file
def getMyNode():
    config = getConfigFile()
    myNodeIP = config['node_ip']
    myNodePort = config['node_port']
    myNodeGeo = config['geo_tag']
    return [myNodeGeo, [myNodeIP, myNodePort]]

#Creating empty file to keep track of if delays are measured or not.
def createEmptyFile():
    fname = 'ef'+getConfigFile()["node_name"] + '.txt'
    f = open(fname, 'w+')
    #Setting Default values
    d = {'isDelayMeasured': 'False'}
    f.write(str(d))
    f.close()
createEmptyFile()
def readEmptyFile():
    fname = 'ef' + getConfigFile()["node_name"] + '.txt'
    f = open(fname, 'r+')
    contents = f.read()
    f.close()
    return eval(contents)
def updateEmptyFile(x):
    fname = 'ef' + getConfigFile()["node_name"] + '.txt'
    f = open(fname, 'w+')
    f.write(str(x))
    f.close()

def cacheFile(filename, region, fileContents):
    path = './cache/'+region+'/'
    # Create cache folder if it is not created.
    if not(os.path.exists('./cache')):
        os.makedirs('./cache')
    # Create respective region as a cache directory to avoid file conflits between different regions
    if not(os.path.exists(path)):
        os.makedirs(path)
    f = open(path+filename, 'wb')
    f.write(fileContents)
    f.close()
    print("Cache Needed, so file cached")
    deleteCacheFile(path, filename)

def deleteCacheFile(path, filename):
    time.sleep(CACHE_TIMEOUT)
    #check if the file exists
    if os.path.exists(path+filename):
        os.remove(path+filename)
        print(path+filename, 'Deleted from cache')
    else:
        print("Cannot delete, File Not found")

def startMeasurements():
    print("Measuring Started")
    measuredDelays = []
    #Send neighbors ping delays one by one
    for i in myNighbors:
        url_server = 'http://' + i[1]+':'+i[2] + '/.ping'
        req = urllib.request.Request(url_server)
        req.add_header('ping', str(myNodeDtl[0]))
        before = time.monotonic()
        print("ping wait...", i[3])
        time.sleep(int(i[3]))
        print("sent", url_server)
        res = urllib.request.urlopen(req)
        after = time.monotonic()
        delay = after - before
        measuredDelays.append([i[0], i[1], i[2], int(delay)])
    #Updating routing table with updated round trip time
    if (createRoutingTable(measuredDelays)):
        updateEmptyFile({'isDelayMeasured': 'True'})
        print("Routing Table created")
    else:
        updateEmptyFile({'isDelayMeasured': 'False'})
        print("Routing Table not created")
    print("Measuring Ended")

#Starting distance vector routing protocol
def startProtocol():
    rTable = readUpdatedRoutingTable()
    for i in rTable:
        sendNeighbors['dvr'].append(
            {'geo_tag': i, 'destination_ip': rTable[i][0][0], 'destination_port': rTable[i][0][1],
             'link_delay': rTable[i][1]})
    sendNeighbors['dvr'].pop(0)
    print("Protocol Started")
    for i in myNighbors:
        url_server = 'http://' + i[1] + ':' + i[2] + '/.calcRoute'
        js = sendNeighbors
        req = urllib.request.Request(url_server, json.dumps(js).encode('utf-8'))
        #sending this node info so that it's neighbors know where the request is coming from
        req.add_header('fromNode', str(myNodeDtl))
        req.add_header('neighbors', str(sendNeighbors))
        print("Sent", url_server, ":", sendNeighbors)
        res = urllib.request.urlopen(req)
    print("Protocol Ended")
#This class handles any incoming requests
class Handler(BaseHTTPRequestHandler):
    myNighbors = getNeighbors()
    rTable = readRoutingTable()
    myNodeDtl = getMyNode()
    sendNeighbors = {'dvr':[]}
    reqDelay = 0 #Delay before it sends any request
    resDelay = 0 #Delay before it sends any response

    #Handler for the GET requests.
    def do_GET(self):
        try:
            if self.path.endswith(".html") or self.path.endswith(".jpg"):
                table = readUpdatedRoutingTable()
                lst = str(self.path).split('/')
                # Region info from URL
                geo_region = lst[len(lst) - 2]
                # Resource info from URL
                resource = lst[len(lst) - 1]
                # Info about where the request came from
                fromNodeInfo = self.headers['from']
                cacheType = self.headers['cacheType']
                if geo_region in table:
                    for i in self.myNighbors:
                        if i[0] == table[geo_region][2][0]:
                            self.reqDelay = int(i[3])
                        if i[0] == fromNodeInfo:
                            self.resDelay = int(i[3])
                    updateLogFile('Request from: ' + fromNodeInfo + '\n---Request HEADERS---\n' + str(self.headers))
                    #Checking if the region info from URL mathes with this node
                    if geo_region == getConfigFile()['geo_tag']:
                        #Checking if the file is present in cache folders of this node
                        if os.path.isfile('./cache/' +geo_region+'/'+ resource):
                            updateLogFile('File Found in '+getConfigFile()['geo_tag']+' Cache')
                            print("Simulated Response Delay", self.resDelay, "Seconds")
                            #wait for response delay
                            time.sleep(self.resDelay)
                            self.send_response(200)
                            #Dynamically determining mimetypes to avoid hardcoding
                            mime_type = mimetypes.MimeTypes().guess_type(resource)[0]
                            self.send_header('Content-type', mime_type)
                            self.send_header('Content-length', str(os.stat('./cache/' + geo_region + '/' + resource).st_size))
                            if cacheType == CACHE_TYPE_TWO:
                                self.send_header(CACHE_NEED_HEADER, 'True')
                            else:
                                self.send_header(CACHE_NEED_HEADER, 'False')
                            self.end_headers()
                            with open('./cache/' +geo_region+'/' + resource, 'rb') as f:
                                self.wfile.write(f.read())
                        else:
                            try:
                                #Connecting to it's content server.
                                nextUrl = 'http://' + getConfigFile()['content_ip'] + ':' + getConfigFile()[
                                    'content_port'] + '/' + resource
                                updateLogFile('File Not Found in '+getConfigFile()['geo_tag']+' Cache\nConnecting to Content Server : ' + nextUrl)
                                req = urllib.request.Request(nextUrl)
                                #Not waiting here for request delay since delay doesn't depend on content server.
                                with urllib.request.urlopen(req) as res:
                                    file = res.read()
                                    hds = res.info()
                                    print(res.info())
                                    updateLogFile('Response From Content Server\n---Response HEADERS---\n' + str(res.info()))
                                    print("Simulated Response Delay", self.resDelay, "Seconds")
                                    time.sleep(self.resDelay)
                                    self.send_response(200)
                                    self.send_header("Content-type", hds['Content-type'])
                                    self.send_header("Content-length", hds['Content-length'])
                                    #Decide if cache is needed or not based on cache type
                                    if cacheType == CACHE_TYPE_ONE:
                                        self.send_header(CACHE_NEED_HEADER, 'True')
                                    else:
                                        self.send_header(CACHE_NEED_HEADER, 'False')
                                    self.end_headers()
                                    #writing the response before cache as it should not depend on it.
                                    self.wfile.write(file)
                                    #Caching the file irrespective of cachetype since in both the cachetypes it caches when taking directly from content server.
                                    #Caching the file as a separate thread since it will serve another request in between if comes.
                                    cacheThread = threading.Thread(target=cacheFile(resource, geo_region, file))
                                    cacheThread.start()
                            except urllib.error.HTTPError:
                                print("File Not Found")
                                self.send_response(404)
                            except urllib.error.URLError:
                                print("URL not found")
                                self.send_response(404)
                    if geo_region != getConfigFile()['geo_tag']:
                        # Checking if the file is present in cache folders of this node
                        if os.path.isfile('./cache/' + geo_region + '/' + resource):
                            updateLogFile('File Found in '+getConfigFile()['geo_tag']+' Cache')
                            print("Simulated Response Delay", self.resDelay, "Seconds")
                            #waiting for response delay
                            time.sleep(self.resDelay)
                            self.send_response(200)
                            #Dynamically determining mimetypes to avoid hardcoding
                            mime_type = mimetypes.MimeTypes().guess_type(resource)[0]
                            self.send_header('Content-type', mime_type)
                            self.send_header('Content-length', str(os.stat('./cache/' + geo_region + '/' + resource).st_size))
                            if cacheType == CACHE_TYPE_TWO:
                                self.send_header(CACHE_NEED_HEADER, 'True')
                            else:
                                self.send_header(CACHE_NEED_HEADER, 'False')
                            self.end_headers()
                            with open('./cache/'+geo_region+'/' + resource, 'rb') as f:
                                self.wfile.write(f.read())
                        else:
                            #Forwarding request to next CDN as filenot found in cache or content server.
                            nextUrl = 'http://' + table[geo_region][2][1][0] + ':' + table[geo_region][2][1][
                                1] + '/' + geo_region + '/' + resource
                            print(nextUrl)
                            updateLogFile('File Not Found in '+getConfigFile()['geo_tag']+' Cache...'+'Forwarding to Next CDN: ' + table[geo_region][2][0])
                            req = urllib.request.Request(nextUrl)
                            req.add_header('from', getConfigFile()['geo_tag'])
                            req.add_header('cacheType', cacheType)
                            print("Simulated Request Delay ", self.reqDelay, "Seconds")
                            #waiting for request delay
                            time.sleep(self.reqDelay)
                            try:
                                with urllib.request.urlopen(req) as res:
                                    file = res.read()
                                    hds = res.info()
                                    print(res.info())
                                    updateLogFile('Response Back from CDN: ' + table[geo_region][2][0] + '\n---Response HEADERS---\n' + str(res.info()))
                                    print("Simulated Response Delay", self.resDelay, "Seconds")
                                    #waiting for response delay before forwarding the responses back
                                    time.sleep(self.resDelay)
                                    self.send_response(200)
                                    self.send_header("Content-type", hds['Content-type'])
                                    self.send_header('Content-length', hds['Content-length'])
                                    if cacheType == CACHE_TYPE_ONE:
                                        self.send_header(CACHE_NEED_HEADER, 'True')
                                    else:
                                        self.send_header(CACHE_NEED_HEADER, 'False')
                                    self.end_headers()
                                    self.wfile.write(file)
                                    #Caching the response as asked in response.
                                    if hds[CACHE_NEED_HEADER]=='True':
                                        cacheThread = threading.Thread(target=cacheFile(resource, geo_region, file))
                                        cacheThread.start()
                                    else:
                                        print("Cache Not needed, so file not cached")
                            except urllib.error.HTTPError:
                                print("File Not Found")
                                self.send_response(404)
                            except urllib.error.URLError:
                                print("URL not found")
                                self.send_response(404)
                else:
                    print("Error Region")
                    self.send_response(404)

            if self.path.endswith(".ping"):
                self.send_response(200)
                ping = self.headers['ping']
                #wait for reponse delays
                for i in self.myNighbors:
                    if i[0] == ping:
                        print("pong wait... ", i[3])
                        time.sleep(int(i[3]))
                self.end_headers()
                measuredDelays = []
                ef_data = readEmptyFile()
                #Checking if it node's neighbor's delays are measured or not.
                # If not starting ping requests to it's neighbors
                if ef_data['isDelayMeasured']=='False':
                    for i in self.myNighbors:
                        url_server = 'http://' + i[1]+':'+i[2] + '/.ping'
                        req = urllib.request.Request(url_server)
                        req.add_header('ping', str(self.myNodeDtl[0]))
                        before = time.monotonic()
                        print("ping wait..", i[3])
                        time.sleep(int(i[3]))
                        print("sent ", url_server)
                        res = urllib.request.urlopen(req)
                        after = time.monotonic()
                        delay = after - before
                        measuredDelays.append([i[0], i[1], i[2], int(delay)])
                    #creating routing table with updated measure delays
                    if (createRoutingTable(measuredDelays)):
                        updateEmptyFile({'isDelayMeasured': 'True'})
                        print("Routing Table created")
                    else:
                        updateEmptyFile({'isDelayMeasured': 'False'})
                        print("Routing Table not created")


            else:
                self.send_response(404)

        except http.client.HTTPException as e:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path.endswith(".calcRoute"):
            #Reading the dvr json from POST request
            content = self.headers['content-length']
            dv = eval(self.rfile.read(int(content)))
            self.rTable = readUpdatedRoutingTable()
            self.send_response(200)
            isUpdate = False
            fromNode = eval(self.headers['fromNode'])
            print(fromNode, ":", dv)
            m = int(self.rTable[fromNode[0]][1])
            for neighbor in dv['dvr']:
                key = neighbor['geo_tag']
                destIp = neighbor['destination_ip']
                destPort = neighbor['destination_port']
                cost = int(neighbor['link_delay'])
                if key in self.rTable:
                    #Calculating Bellman Ford's lowest cost(RTT) and updating.
                    if (cost + m) < int(self.rTable[key][1]):
                        self.rTable[key][0][0] = destIp
                        self.rTable[key][0][1] = destPort
                        self.rTable[key][1] = cost + m
                        self.rTable[key][2] = fromNode
                        isUpdate = True
                        print("Route Updated")
                else:
                    #Adding new route to the node
                    self.rTable[key] = [[destIp, destPort], cost + m, fromNode]
                    isUpdate = True
                    print("Route added and Updated")
            updateRoutingTable(self.rTable)
            print("Routing Table", readRoutingTable())
            #Trigger requests to it's neighbor when the routes are updated.
            if isUpdate:
                self.sendNeighbors = {'dvr':[]}
                for i in self.rTable:
                    self.sendNeighbors['dvr'].append(
                        {'geo_tag': i, 'destination_ip': self.rTable[i][0][0], 'destination_port': self.rTable[i][0][1],
                         'link_delay': self.rTable[i][1]})
                #Popping the first element as it is neighbor to itself
                self.sendNeighbors['dvr'].pop(0)
                print("Sending Vectors :", self.sendNeighbors)
                for i in self.myNighbors:
                    url_server = 'http://' + i[1] + ':' + i[2] + '/.calcRoute'
                    js = self.sendNeighbors
                    #Sending encoded json in POST request.
                    req = urllib.request.Request(url_server, json.dumps(js).encode('utf-8'))
                    req.add_header('fromNode', str(self.myNodeDtl))
                    req.add_header('neighbors', str(self.sendNeighbors))
                    print("Sent", url_server, ":", self.sendNeighbors)
                    try:
                        res = urllib.request.urlopen(req)
                    except urllib.error.HTTPError:
                        print("File Not Found")
                        self.send_response(404)
                    except urllib.error.URLError:
                        print("URL not found")
                        self.send_response(404)


            else:
                print("No Route Update")
            self.end_headers()
            print("Done after sending Vectors")


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

#Server start method in a separate thread as it should not depend on startMeasurements() and startProtocol() methods.
def startServer():
    try:
        server = ThreadedHTTPServer((SERVER_IP, PROXY_PORT), Handler)
        print("Server Started on port: %s" % PROXY_PORT)
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
    except KeyboardInterrupt:
        print("Interrupted")
        server.socket.close()

if __name__ == '__main__':
    myNighbors = getNeighbors()
    fileName = 'RT_' + getConfigFile()["node_name"] + '.txt'
    rTable = readRoutingTable()
    myNodeDtl = getMyNode()
    sendNeighbors = {'dvr': []}
    initialDelay = random.randint(10, 20)
    #A random initial wait between 10 to 20 seconds so that in between it's neighbor CDN servers start running.
    print('I am going to wait a random', initialDelay, 'seconds so that my neighbors are active')
    time.sleep(initialDelay)
    startServer()
    while HEART_BEATS:
        try:
            #An independent delay measuring thread
            delaythread = threading.Thread(target=startMeasurements())
            delaythread.start()
            #waiting 100 fixed seconds so that delays between CDNs are measured before Distance Vector Protocol starts.
            time.sleep(100)
            protocolThread = threading.Thread(target=startProtocol())
            protocolThread.start()
            #Repeating measurements and updating routes by running protocol frequently for like every 10 minutes
            time.sleep(HEART_BEAT_TIMEOUT)

        except urllib.error.URLError as e:
            #Retrying to connect to it's neighbors before start measuring delays and protocol
            print("Hey one of your neighbors is inactive trying again in 5 seconds")
            time.sleep(5)

