import numpy as np

v8 = 0x19a68495
v6 = 0x19a68495
v5 = 0
args = np.array([v8, v6, v5], dtype=np.uint64)


a3 = 0x01071984  # const

args[0] += (a3 + 4 * (args[2] & 3)) + (args[2] ^ args[1]) + ((args[1] >> 5) ^ 16 * args[1])

v5 -= 0x61c88647
"""
a = (v8 * 16) & 0xFFFFFFFF
#print("a =", hex(a))
b = (v8 >> 5) & 0xFFFFFFFF
#print("b =", hex(b))
ab = (a ^ b) & 0xFFFFFFFF
#print("ab =", hex(ab))

c = (v5 ^ v8) & 0xffffffff
#print("c =", hex(c))

p = (ab + c) & 0xffffffff
#print("p =", hex(p))

d = (v5 >> 11) & 0xffffffff
#print("d =", hex(d))
d = (d & 3) & 0xffffffff
#print("d =", hex(d))
d = (4 * d) & 0xffffffff
d = (a3 + d) & 0xffffffff
k = (p + d) & 0xfffffff
#print("k =", hex(k))
#print("k =", hex(k))

v6 += k
"""
print(hex(args[0]))
print(hex(v5))

# 0x577c46b1


