import numpy as np

v8 = np.uint32(0x19a68495)
v6 = np.uint32(0x19a68495)
v5 = np.uint32(0)
a3 = [np.uint32(0x01071984),
      np.uint32(0x12221959),
      np.uint32(0x12301958),
      np.uint32(0x03191960)]

for i in range(32):
    v8 = np.uint32(v8 + a3[v5 & 3] + (v5 ^ v6) + ((v6 >> 5) ^ np.uint32(16 * v6)))
    v5 = np.uint32(v5 - 1640531527)
    v6 = np.uint32(v6 + a3[(v5 >> 11) & 3] + (v5 ^ v8) + ((v8 >> 5) ^ np.uint32(16 * v8)))

print(hex(v8))
print(hex(v6))


