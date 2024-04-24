import os
from PIL import Image
import math
import socket as s


# Step 1
def image_to_bits(image_path):
    with Image.open(image_path) as img:
        width, height = img.size
        pixels = img.convert('1').load()
        bits = ''
        for y in range(height):
            for x in range(width):
                bits += '1' if pixels[x, y] else '0'
    return bits


def divide_bits_into_chunks(file_id, bits, chunk_size, num_of_chunks):
    packet_id = 0
    packets = []
    for i in range (math.ceil(num_of_chunks)):
        if i != math.ceil(num_of_chunks)-1:
            packets.append(str(bin(i)[2:].zfill(16)) +  str(bin(file_id)[2:].zfill(16)) + bits[0:chunk_size] + str(bin(0x0000)[2:].zfill(32)))
        else:
            packets.append(str(bin(i)[2:].zfill(16)) +  str(bin(file_id)[2:].zfill(16)) + bits[0:chunk_size] + str(bin(0xFFFF)[2:].zfill(32)))
        bits = bits[chunk_size:]
    return packets

# main Step 1
image_path = 'C:\\Users\\salma\\Downloads\\small file.jpeg'
bits = image_to_bits(image_path)
chunk_size = 1000
file_id = 0
num_of_chunks = len(bits) / chunk_size
packets = divide_bits_into_chunks(file_id, bits, chunk_size, num_of_chunks)
# print(packets[-1])



s1 = s.socket(s.AF_INET, s.SOCK_DGRAM)
port = 12345

s1.bind(('127.0.0.1', port))

for i in range (len(packets)):
    data, addr = s1.recvfrom(4064)
    s1.sendto(packets[i].encode(), addr)