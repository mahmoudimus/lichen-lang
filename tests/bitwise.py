def encode(value):
    return ((value & 8) << 4) | ((value & 4) << 3) | ((value & 2) << 2) | ((value & 1) << 1)

print encode(15)    # 170
print encode(8)     # 128
print encode(2)     # 8
print encode(0)     # 0
