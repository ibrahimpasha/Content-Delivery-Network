### Content Delivery Network
Network of CDN nodes distributed geographically among six regions africa, antarctica, asia, europe, northamerica, southamerica to deliver content relatively at high performance to end user with shortest path using Distance Vector Routing algorithm. Each CDN node has its own content server connected to it to server files. Each CDN node has cache storage to keep the contents for a period of time.
#### Topology:
![alt text](https://github.com/ibrahimpasha/Content-Delivery-Network/blob/master/topology.PNG)

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
