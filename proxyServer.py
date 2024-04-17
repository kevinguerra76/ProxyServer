from socket import *
import sys
import select #needed for select.select
import os
import time

#Kevin Guerra CS 5313 Computer Networks
#Implementing a Simple HTTP Proxy Server

CACHE = "cache" #Global variable for caching

#This function will get the filetouse
def get_url(message):
    try:
        #If the file is less than the minimum len of 'GET www.'
        if(len(message)< 8): return None
        
        #The message is formatted in such a way:
        '''
        Client Message:
        GET /www.tizag.com/htmlT/images.php HTTP/1.1
        Host: localhost:8888
        Connection: keep-alive
        Cache-Control: max-age=0
        ...
        '''
        #What I have to extract is the url that is in the same line as GET
        #To do so I will find 'GET' then find the first apperance of a '.'
    
        get_loc = message.find('GET')
        if(get_loc == -1): 
            raise Exception()  #If there is no GET then there was an error
            
        #I now look for the first appearance of www.
        www_loc = message.find('www.')
        if(www_loc == -1): 
            raise Exception()
        url = message[www_loc + 4:]
        #print(message[www_loc + 4:])
        #Just in case of extra information at the end I will find the first space ' ' or first '/'
        space = url.find(' ')
        slash = url.find('/')
        if(slash < space ):
            return url[:slash]
        return url[:space]
        
    except:
        print('Not a valid input')
        return None
    
def add_to_cache(filename, response, specified_time = None):
    #I will open a file to write on
    with open(os.path.join(CACHE, filename), "wb") as f:
        f.write(response)
    if not time == None:
        timer(filename, specified_time)

def timer(filename, specified_time):
    #implement time
    #Delete the file after the time passes
    time.sleep(specified_time) #After enough time passes this will trigger and delete
    try:
        os.remove(os.path.join(CACHE, filename))
        print(filename, 'expired and removed.')
    except OSError:
        print('Error removing cache entry:',filename)

if __name__ == "__main__":
    
    if len(sys.argv) <= 1:
    	print('Usage : "python ProxyServer.py server_ip"\n[server_ip : It is the IP Address Of Proxy Server')
    	sys.exit(2)
    	print('Usage : "python ProxyServer.py server_ip"\n[server_ip : It is the IP Address Of Proxy Server')
    	sys.exit(2)
    	
    # The proxy server is listening at 8888 
    tcpSerSock = socket(AF_INET, SOCK_STREAM)
    #print(sys.argv[1])
    tcpSerSock.bind((sys.argv[1], 8888)) #This is my own IP/Local Host
    tcpSerSock.listen(100)
    
    #If user gave a second argument, that will be the time for the cache
    cache_time = None
    if(len(sys.argv) > 2):
        cache_time = sys.argv[2]

    #cache = set()  #For now I will let the cache behave a set meaning it is only stored locally in each call
    
    while 1:
    	# Strat receiving data from the client
        print('Ready to serve...')
    	## FILL IN HERE...
        tcpCliSock, addr = tcpSerSock.accept()
        print('Received a connection from:', addr) 
    
        message = tcpCliSock.recv(1024)
        
        #print('Client Message:\n',message)
    	# Extract the filename from the given message
        #To do this I made a function called get_url() after many failed attempts
    
        decoded_message = message.decode()
        filetouse = get_url(decoded_message) ## FILL IN HERE...
        if(filetouse == None):
            #print('An Error Occured')
            continue
        #filetouse = message
        #print('\nTouse;')
        #print(filetouse)
        #print('end touse')
        
        #print ("\n[GET Request] \nRequest body: \n", filetouse, "\n")
        
        #print('--------------')
        #print('url:',filetouse[7:-1]) #Find the url after the http:// and without the final /
        #print('--------------')
        
        url = filetouse
        send_me = decoded_message[:decoded_message.find('host:8888') + len('host:8888')]
        #send_me = decoded_message
        
        print('THIS URL WILL BE USED', url)
        
        try:
    		# Check wether the file exist in the cache
            fileExist = "false" #If the file IS found then it will be true at the bottom
    		## FILL IN HERE...
            with open(filetouse, "r") as f:
                for line in f:
                    tcpCliSock.send(line.encode())
        
                fileExist = "true"
        		# ProxyServer finds a cache hit and generates a response message
                tcpCliSock.send(("HTTP/1.0 200 OK\r\n").encode())          
                tcpCliSock.send(("Content-Type:text/html\r\n").encode()) 
                
    
    
    	# Error handling for file not found in cache, need to talk to origin server and get the file
        except IOError:     
            print('File not found in Cache')
            print('-----------------')
            print('Request to Origin Below:')
            print(send_me)
            print('-----------------')
            if fileExist == "false": 
                try:
                    print('Attempting to connect to url')
                    #FILL IN HERE...
                    #Need to establish connection to the server using filetouse
                    originSock = socket(AF_INET, SOCK_STREAM)
                    #print(url)
                    originSock.connect((url, 80))
                    print('**made originsocket**')
                    
                    originSock.send(send_me.encode())
                    print('**message sent**')
                       
                    originSock.settimeout(10)  # Set a timeout of 10 seconds
                    try:
                        response = originSock.recv(4096)
                    except:
                        print('socket took to long to respond')
                    #response = "RESPONSE".encode()
                    print('**response recieved**')
                    print('ORIGIN SOCKET RESPONSE:')
                    print(response)
                    
                    tcpCliSock.send(response)
                    #if successful add to cache
                    
                    #Implement Cache
                    #I will write a file with the name as filetouse
                    #The inside of the file will be the message 
                    #It will also have a timer and when it expires it deletes itself
                    add_to_cache(url, response, cache_time)
                
                except:
                    print("Illegal request")                                               
            else:
    			# HTTP response message for file not found
                tcpCliSock.send(("HTTP/1.0 404 sendErrorErrorError\r\n").encode())                               
                tcpCliSock.send(("Content-Type:text/html\r\n").encode()) 
                tcpCliSock.send(("\r\n").encode()) 
    
    	# Close the client and the server sockets    
        tcpCliSock.close() 
    tcpSerSock.close()
