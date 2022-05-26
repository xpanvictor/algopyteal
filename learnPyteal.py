from pyteal import *

x = Bytes("Content")
y = Concat(Bytes("example "), x)

# print(y)

z = Substring(y, Int(2), Len(y))

# Logging to the chain
Log(x)
