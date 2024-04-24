import socket
import os
from PIL import Image
import math

def image_to_bits(image_path):
    with Image.open(image_path) as img:
        width, height = img.size
        pixels = img.convert('1').load()
        bits = ''
        for y in range(height):
            for x in range(width):
                bits += '1' if pixels[x, y] else '0'
    return bits



def create_sender_packet(packet_id, file_id, data_chunk, is_last_chunk):
    if is_last_chunk:
        trailer = 0xFFFF
    else:
        trailer = 0x0000
    return packet_id.to_bytes(2, byteorder='big') + file_id.to_bytes(2, byteorder='big') + data_chunk + trailer.to_bytes(2, byteorder='big')

def divide_bits_into_chunks(bits, chunk_size, num_of_chunks):
    file_id = 0
    packet_id = 0
    packets = []
    for i in range (math.ceil(num_of_chunks)):
        packets.append(bits[0:chunk_size])
        bits = bits[chunk_size:]
    return packets


image_path = 'C:\\Users\\salma\\Downloads\\small file.jpeg'
bits = image_to_bits(image_path)
chunk_size = 1000
num_of_chunks = len(bits) / chunk_size
pakets = divide_bits_into_chunks(bits, chunk_size, num_of_chunks)


# Example usage
# file_path = "C:\\Users\\salma\\Downloads\\small file.jpeg"
# chunk_size = 1000  # MSS
# Number_chunks = 5
# packets = divide_file_into_chunks(file_path, chunk_size, Number_chunks)
# # for packet in packets:
# #     print(packet.hex())
