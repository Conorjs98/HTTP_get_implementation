"""
Name: Conor Stripling
Section: 002
UCID: cs439

"""

import sys, os, datetime, time
from socket import *

# get command line arguments
usr = sys.argv
host = sys.argv[1]
port = int(sys.argv[2])

# create socket, bind it, listen
sock = socket(AF_INET, SOCK_STREAM)
sock.bind((host, port))
sock.listen(1)
datalen = 10000
print("Server listening on port: ", str(port))


# opening a file and reading it in python https://stackoverflow.com/questions/18256363/how-do-i-print-the-content-of-a-txt-file-in-python
def getcontents(filename_):
    f = open(filename_, 'r')
    contents = f.read()
    f.close()
    return contents


# get last modified date and convert it into correct time zone
def getmod(filename):
    secs = os.path.getmtime(filename)
    modtime = time.gmtime(secs)
    last_mod_time = time.strftime("%a, %d %b %Y %H:%M:%S GMT", modtime)
    return last_mod_time


while True:
    # create connection with client
    connectionSocket, address = sock.accept()
    print("Socket established with: " + address[0] + " " + str(address[1]))
    data = connectionSocket.recv(datalen).decode()
    request = data.split()
    # make sure it is a GET request being received, this will ignore any other HTTP requests besides GET
    if request[0] == "GET":
        conditionalGET = False
        # check for conditional GET, set boolean variable for it
        count = 0
        for line in data.split("\r\n"):
            count += 1
        if count == 5:
            conditionalGET = True

        # get file name remove path
        filename = request[1]
        filename = filename.split("/")

        # get current date and time
        t = datetime.datetime.utcnow()
        date = t.strftime("%a, %d %b %Y %H:%M:%S GMT")

        # attempt to send get response, catch exception if file does not exist
        try:
            filecontents = getcontents(filename[1])
            lastmodified = getmod(filename[1])

            # send respoonse based on GET request type
            if conditionalGET:
                # array to pull the modified since date
                dataArray = data.split("\r\n")
                dateArray = dataArray[2].split("If-Modified-Since: ")
                clientModified = dateArray[1]
                if clientModified == lastmodified:
                    getresponse = "HTTP/1.1 304 Not Modified\r\n" + "Date: " + date + "\r\n\r\n"
                else:
                    getresponse = "HTTP/1.1 200 OK\r\n" + "Date: " + date + "\r\nLast-Modified: " + lastmodified + "\r\nContent-Length: " + str( 
                        len(filecontents)) + "\r\nContent-Type: text/html; charset=UTF-8\r\n\r\n" + filecontents
            else:
                getresponse = "HTTP/1.1 200 OK\r\n" + "Date: " + date + "\r\nLast-Modified: " + lastmodified + "\r\nContent-Length: " + str(
                    len(filecontents)) + "\r\nContent-Type: text/html; charset=UTF-8\r\n\r\n" + filecontents
        except IOError:
            getresponse = "HTTP/1.1 404 Not Found\r\n" + "Date: " + date + "\r\n\r\n"
        connectionSocket.send(getresponse.encode())
        print("Content Sent")
