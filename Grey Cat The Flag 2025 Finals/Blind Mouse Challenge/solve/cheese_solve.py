import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('challs.nusgreyhats.org',33301))

sock.recv(1024).decode()
sock.send("F\n".encode())
ct = sock.recv(1024).decode()[17:50]
print("Target:\n" + ct + "\n")

sock.send("M\n".encode())
sock.recv(1024).decode()
sock.send((ct+"\n").encode())
pt = sock.recv(1024).decode()[17:50]
print("(Almost correct) Flag:\n" + pt + "\n")
# grey{pR3t7y_5urE_c4n_8rUT3_f0rC3^
sock.shutdown(0)