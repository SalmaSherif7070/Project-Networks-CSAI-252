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

# main Step 1
image_path = 'C:\\Users\\salma\\Downloads\\small file.jpeg'
bits = image_to_bits(image_path)
chunk_size = 1000
file_id = 0
num_of_chunks = len(bits) / chunk_size
packets = divide_bits_into_chunks(file_id, bits, chunk_size, num_of_chunks)
# print(packets[-1])

window_size = 3
back_iterations = math.ceil(len(packets)/window_size)


# ... [rest of your sender code] ...

s1 = s.socket(s.AF_INET, s.SOCK_DGRAM)
port = 12345
addr = ('127.0.0.1', port)

# Initialize the base and next sequence number
base = 0
next_seq_num = 0
window_size = 3
timeout = 0.5  # Set a timeout value for retransmission

# Function to start a timer for the oldest unacknowledged packet
def start_timer():
    return time.time()

# Function to check if the timer has expired
def timer_expired(start_time):
    return time.time() - start_time > timeout

# Start the timer
timer = start_timer()

while base < len(packets):
    # Send all packets in the window
    while next_seq_num < base + window_size and next_seq_num < len(packets):
        s1.sendto(packets[next_seq_num].encode(), addr)
        print("Sending packet ", next_seq_num)
        next_seq_num += 1

    # Wait for acknowledgment or timeout
    while True:
        try:
            s1.settimeout(timeout)
            ack, _ = s1.recvfrom(4096)
            ack_num = int(ack.decode().split()[-1])  # Extract the packet number from the acknowledgment
            print(f"Acknowledgment received for packet {ack_num}")

            # Move the window if the acknowledgment is for the base packet
            if ack_num >= base:
                base = ack_num + 1
                timer = start_timer()  # Reset the timer
            if all(ack[base:base+window_size]):
                break  # Break the inner loop and send the next window
            
        except s.timeout:
            # If timeout occurs, go back to the base and resend all packets in the window
            print("Timeout occurred, resending window")
            next_seq_num = base
            break  # Break the inner loop to resend the packets

s1.close()  # Don't forget to close the socket
