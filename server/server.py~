#server.py
import socket
host = 'localhost'
port = 11122

serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serversock.bind((host,port))
serversock.listen(1)
print 'Waiting for connections...'
clientsock, client_address = serversock.accept()

while True:
    rcvmsg = clientsock.recv(1024)
    print 'Received -> %s' % (rcvmsg)
    if rcvmsg == '':
      break
    print 'Type message...'
    s_msg = raw_input()
    if s_msg == '':
      break
    print 'Wait...'

    clientsock.sendall(s_msg) 
clientsock.close()
