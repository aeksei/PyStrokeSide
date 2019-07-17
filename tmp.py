import numpy as np

v8 = 0x19a68495
v6 = 0x19a68495
a3 = [0x01071984, 0x12221959, 0x12301958, 0x03191960]


args = np.array([v8, v6, 0], dtype=np.uint32)


# args[0] += (a3 + 4 * (args[2] & 3)) + (args[2] ^ args[1]) + ((args[1] >> 5) ^ 16 * args[1])

k1 = a3 + np.left_shift(np.bitwise_and(args[2], 3), 2)

k2 = np.bitwise_xor(args[2], args[1])

k3 = np.bitwise_xor(np.right_shift(args[1], 5),
                    np.left_shift(args[1], 4))

args[0] = np.bitwise_and(args[0] + (k1 + k2 + k3), 0xffffffff)

args[2] -= 0x61c88647
print(args[2])
k3 = np.bitwise_xor(np.right_shift(args[0], 5),
                    np.left_shift(args[0], 4))

k2 = np.bitwise_xor(args[2], args[0])

k1 = a3 + np.left_shift(np.bitwise_and(np.right_shift(args[2], 11), 3), 2)




# 0x577c46b1
8200-000320-027


