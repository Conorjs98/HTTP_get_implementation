"""
Name: Conor Stripling
Section: 002
UCID: cs439

"""

import sys, re, os
from socket import *

# check to see if a cache exists, if not make one
try:
    f = open("cache.txt", "r")
except IOError:
    f = open("cache.txt", "w+")
    f.close()
    f = open("cache.txt", "r")

# command line argument split into array "arguments"
usr = sys.argv
url = sys.argv[1]
arguments = re.split('[:/]', url)
host = arguments[0]
port = arguments[1]
file = arguments[2]

# check to see if file is cached, looping through file found at https://stackoverflow.com/questions/13546809/python-reading-each-string-in-a-file
cached = False
line = f.readline()
linecount = 0
while line:
    thisline = line.split(" ", 1)
    for string in thisline:
        if string == file:
            cached = True
            cachedline = line.split(" ", 1)
    linecount += 1
    line = f.readline()
f.close()

# if cached create conditional GET if not cached use regular get
if cached:
    # get last cached time
    lastcachedtime = cachedline[1]
    getrequest = "GET /" + file + " HTTP/1.1\r\nHost: " + host + ":" + port + "\r\n" + "If-Modified-Since: " + lastcachedtime + "\r\n\r\n"
else:
    getrequest = "GET /" + file + " HTTP/1.1\r\nHost: " + host + ":" + port + "\r\n\r\n"

# create socket, receive data
buffersize = 1000
sock = socket(AF_INET, SOCK_STREAM)
print(getrequest)
sock.connect((host, int(port)))
sock.send(getrequest.encode())
recvdata = sock.recv(buffersize)
recvdata = recvdata.decode()
print(recvdata)

# check for return code
httpResp = recvdata.split()
returncode = httpResp[1]

# check for successful return code
if int(returncode) == 200:
    recvdata = recvdata.split("\r\n")
    recvdataTime = recvdata[2].split("Last-Modified: ")
    lastmodtime = recvdataTime[1]

    # get file contents into variable
    filecontents = recvdata[6]

    # create the actual cached file
    f = open("cached_" + file, "w+")
    f.write(filecontents)
    f.close()
    # replace last mod time in cache.txt with most recent mod time at https://stackoverflow.com/questions/34259452/python-3-search-and-replace-text-file
    if cached:
        with open("cache.txt", "r") as f:
            update = f.read()
        update = update.replace(str(lastcachedtime), str(lastmodtime))
        with open("cache.txt", "w") as f:
            f.write(update)
    else:
        # add cache file name and mod time to cache.txt if it was not already there
        f = open("cache.txt", "a")
        f.write("\n" + file + " " + str(lastmodtime))
        f.close()
elif int(returncode) == 304:
    # print the contents of the cached file
    f = open("cached_" + file, 'r')
    contents = f.read()
    f.close()
    print(contents)

sock.close()
