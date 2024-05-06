import os
from PIL import Image
import math
import socket as s
import time


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


image_path = "C:\\Users\\salma\\OneDrive\\Desktop\\UNI\\Spring 2024\\Network\\Project Networks CSAI 252\\images\\small file.jpeg"
bits = image_to_bits(image_path)
chunk_size = 1000
file_id = 0
num_of_chunks = len(bits) / chunk_size
packets = divide_bits_into_chunks(file_id, bits, chunk_size, num_of_chunks)



s1 = s.socket(s.AF_INET, s.SOCK_DGRAM)
port = 12345
addr = ('127.0.0.1', port)

base = 0
next_packet_num = 0
window_size = 3
timeout = 0.5

def start_timer():
    return time.time()

pre_ack = -1


timer = start_timer()

while base < len(packets):
    # Send all packets in the window
    while next_packet_num < base + window_size and next_packet_num < len(packets):
        s1.sendto(packets[next_packet_num].encode(), addr)
        print("Sending packet ", next_packet_num)
        next_packet_num += 1

    # Wait for acknowledgment + move window or timeout
    while True:
        try:
            s1.settimeout(timeout)
            ack, _ = s1.recvfrom(4096)
            ack_num = int(ack.decode())
            print(f"Acknowledgment received for packet {ack.decode()}")
            # if pre_ack == ack:


            # Move step if recieved ack + Reset the timer
            if ack_num >= base:
                base = ack_num + 1
                timer = start_timer()  
            
            # return True unless the ack not recieved
            if all(ack[base:base+window_size]):
                break  
            
        except s.timeout:
            # Did not recive ack -> start sending again from base
            print("Timeout occurred, resending window")
            next_packet_num = base
            break

s1.close()
