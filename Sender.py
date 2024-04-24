import socket
import os
from PIL import Image
import math



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
            packets.append({"Packet ID": i, "File ID": file_id, "Application Data" : bits[0:chunk_size], "Trailer": 0x0000})
        else:
            packets.append({"Packet ID": i, "File ID": file_id,"Application Data" : bits[0:chunk_size], "Trailer": 0xFFFF})
        bits = bits[chunk_size:]
    return packets

# main Step 1
image_path = 'C:\\Users\\salma\\Downloads\\small file.jpeg'
bits = image_to_bits(image_path)
chunk_size = 1000
file_id = 0
num_of_chunks = len(bits) / chunk_size
pakets = divide_bits_into_chunks(file_id, bits, chunk_size, num_of_chunks)
print(pakets)
