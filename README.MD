### Content Delivery Network
Network of CDN nodes distributed geographically among six regions africa, antarctica, asia, europe, northamerica, southamerica to deliver content relatively at high performance to end user with shortest path using Distance Vector Routing algorithm. Each CDN node has its own content server connected to it to server files. Each CDN node has cache storage to keep the contents for a period of time.
#### Topology:
![alt text](https://github.com/ibrahimpasha/Content-Delivery-Network/blob/master/topology.PNG)

#### Introduction:
Content Delivery Network is a geographically distributed group of servers which work together to
provide fast delivery of internet content. A CDN does not host content but it does help cache content at
network edge which improves website performance by means of increasing content availability,
improving the website load times and reducing the band with costs. Thus, by implementing different
cache schemes, providing the internet content closer to the end user.
#### Design:
Fig(a): Topology of CDN servers with proxy, delay information, content-servers, cache storage.
![alt text](https://github.com/ibrahimpasha/Content-Delivery-Network/blob/master/topology.PNG)
Designed CDN, is a network of six geographically interconnected regions namely africa, antarctica, asia,
europe, northamerica and southamerica to deliver content relatively with high performance to end user.
Each CDN server is connected to its neighbor CDN servers and will have delay information to send packets
to its neighbors which will be provided in configuration file. Also, Each CDN node has its own content
server connected to it which serves content and Each CDN node has cache storage to keep the contents
for a period of time. A proxy server will be connected to one of the CDN servers and will take request
directly from the client and forwards it.
Each CDN node will find the Round-Trip Time to its neighbor CDN servers and will use it to find the shortest
paths with least latency to all the CDN servers using Distance Vector Routing algorithm. The response
forwarding in the CDN network is done along the same path as the request forwarding. For the cache
design, there will be two types of cache schemes,
1. ‘type1’: Caches the response along each node as it is forwarded to the origin of request. (for
instance, if the request to Europe content server is raised, it caches the content at Europe, Asia,
and Africa CDNs in a single request.)
2. ‘type2’: Caches the response just on the first hop that does not have the content on the cache yet
when the response is forwarded. (for instance, if the request to Europe content server is raised,
it first caches at Europe CDN, then at Asia CDN in second request, then at Africa CDN in third
request).
#### Implementation:
Measuring Delays: Each CDN node will have its configuration file in which it will have its geographical
region information that identifies its location and IP address and port details to its content server, and
also links details to its neighbour CDN servers. When the CDN starts running it will start measuring the
Round-Trip Time to its neighbours by sending a GET request ‘ping’. Both the CDNs will wait for a delay
time to its neighbours mentioned in the config file while sending and receiving the request.
Distance Vector Routing Algorithm: After all CDN servers finish finding the RTT, they will start running
the Distance Vector Routing Protocol to find the shortest path to all the CDN servers by Bellman Ford’s
principle dx(y) = min {c(x,v) + dv(y)}. Where dx(y) = cost of least-cost path from X to Y. Each CDN will
maintain a routing table and shares it with its neighbors and when each CDN node finds the least RTT to
another node, routing table gets updated. After a node updates its routing table, it immediately shares
the updated routing table with its neighbor CDN servers. When every node has updated routing table, it
will have the shortest path to all the other CDN servers.
Proxy and Content Servers: Content servers will be connected to its CDN servers and serve the
requested files without any delay. Proxy server is connected to one of the CDN server which is
mentioned when it is getting started and will also have type of cache that it wants to use.
Caching: Once, every servers starts ready to serve the requests, Client will request a hostname (e. g. ,
http://europe/fileD.html )which indicates the region where the HTTP server is located. The browser
connects to a proxy which forwards the request to the CDN server it is connected to. The CDN server
then decides if it should fetch this file directly from the Content Server or through the CDN network,
which is decided by type of cache scheme that is requested to use.
When the CDN server gets the request, it checks region info from hostname and if it is the designated
region to serve the content, it will check the following conditions…
1. If the requested content is in cache memory, it writes the response back.
2. If the requested content is not in cache memory, it will forward the request to content server
and gets the file if it exists there and caches the content for a 100 second of time based on type
of cache.
If the CDN server is not the designated region to serve the content, it will check following conditions…
1. If the requested content is in cache memory, it writes the response back.
2. If the requested content is not in cache memory, it forwards the request to next CDN server
which is in shortest path (gets this info from routing table) and caches the response for a 100
second of time based on type of cache.

#### Logging: Whenever a CDN server gets a request it logs request info such as where the request is coming
from, request headers and to where the next request heading to. And while getting a response it logs
info about response headers and content cache information at CDN.
New Features: Few small features added are…
1. While caching the content, if two different region CDN server have same file named contents,
file name conflicts arise even though two files are different. To resolve this issue, I have
maintained individual cache storage for each region.
2. While serving the different types of files, maintaining mimetype for Content-type implemented
dynamically without hardcoding.
Measurements: For Instance request from the client is http://europe/fileD.html, the shortest path
would be… Browser---> Proxy ---> Africa ---> Asia ---> Europe ---> Content Server.


#### Steps to run
There are 6 folders for 6 different regions for simulating the environment. Every region has same cdn.py and contentServer.py file but have different config.json files.
Follow the below procedure to run the source code in different terminals.

#### Steps to run Content server
```python3 contentServer.py <content-server-port>```

For Instance, go to content_server directory in each region and run the commands separately
```
python3 contentServer.py 20231
python3 contentServer.py 20232
python3 contentServer.py 20233
python3 contentServer.py 20234
python3 contentServer.py 20235
python3 contentServer.py 20236
```

#### Steps to run CDN server
```python3 cdn.py <CDN-port> <config-file>```

For instance, go to root of each region directory and run the commands separately
```
python3 cdn.py 20221 config.json
python3 cdn.py 20222 config.json
python3 cdn.py 20223 config.json
python3 cdn.py 20224 config.json
python3 cdn.py 20225 config.json
python3 cdn.py 20226 config.json
```

#### Steps to run Proxy server
```python3 proxy.py <proxy-port> <server-ip> <server-port> <type of cache ('type1' or 'type2')> ```

For instance, run the following command in terminal
```
python3 proxy.py 20220 program.cs.uh.edu 20221 type1
or
python3 proxy.py 20220 program.cs.uh.edu 20221 type2
```

##### Author:
Ibrahim Mohammad

imohammad@uh.edu 

+1-713-366-2544 

University of Houston.
