# [CRYPTO] Blind Mouse Challenge

## Description

Run around like a blind mouse... can you decrypt the flag?

Distrib: No dist

### Flag

`grey{pR3t7y_5urE_c4n_8rUT3_f0rC3}`

## Intended Solution

This challenge is an unknown encryption scheme with an Encryption Oracle. The intended solve was to bruteforce the characters one by one using the encryption oracle. The encryption scheme uses Cipher Block Chaining (CBC), with each block being one character wide. Therefore, the service needs to be restarted after every failed attempt at bruteforcing the flag.

### Solve Script

```python
import socket

start_sock = lambda: (sock:=socket.socket(socket.AF_INET, socket.SOCK_STREAM), 
                      sock.connect(('challs.nusgreyhats.org',33301)), 
                      sock)[2]

sock = start_sock()

sock.recv(1024).decode()
sock.send("F\n".encode())
ct = sock.recv(1024).decode()[17:50]
print("Target:\n" + ct + "\n")
sock.shutdown(0)

chars = "_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789}"
ind = 0
flag = "grey{"
while flag[-1] != "}":
    sock = start_sock()
    sock.recv(1024).decode()
    sock.send("M\n".encode())
    sock.recv(1024).decode()

    sock.send((flag + chars[ind] + "\n").encode())
    t = sock.recv(1024).decode()[17:18+len(flag)]
    if ct.startswith(t):
        print(f'{t:<{len(ct)}} | {flag}')
        flag += chars[ind]
        ind = 0
        continue
    ind += 1
    if ind == len(chars):
        break
    sock.shutdown(0)

print(f'Flag is {flag}')
# grey{pR3t7y_5urE_c4n_8rUT3_f0rC3}
```

## Cheese (Pun intended.)

The encryption scheme uses a pretty poor XOR encryption that is not surjective:

```python
class Blind:
    def __init__(self):
        self.iv = 0

    def encrypt(self, msg):
        res = ""
        for c in msg:
            res += chr(self._encrypt_single(c))
        return res

    def _encrypt_single(self, char):
        if type(char) != int:
            char = ord(char) - 31
        res = (char ^ self.iv) % 95
        self.iv += 1
        return res + 31
```

In order to not have any ambiguity with the flag, I ensured that there are no alternative "options" for all the characters, but in doing so, I made the encryption (essentially) its own inverse.

```python
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
sock.shutdown(0)
```

By feeding the encrypted flag back into the encryption oracle, you can get an almost correct flag. By fixing the last character to be `}`, you get the flag `grey{pR3t7y_5urE_c4n_8rUT3_f0rC3}`.

Solve scripts: [intended_solve.py](https://raw.githubusercontent.com/k-hian/CTFWriteups/refs/heads/main/Grey%20Cat%20The%20Flag%202025/Blind%20Mouse%20Challenge/solve/intended_solve.py) [cheese_solve.py](https://raw.githubusercontent.com/k-hian/CTFWriteups/refs/heads/main/Grey%20Cat%20The%20Flag%202025/Blind%20Mouse%20Challenge/solve/cheese_solve.py)

## Thoughts

Small oops regarding the XOR inverse, but at least it is not obvious since the encryption scheme is not provided. Also intended to be easy, so expected 20/20 solves.