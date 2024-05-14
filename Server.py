import os
from PIL import Image
import math
import socket as s
import time
import datetime
import cv2
import numpy as np

# Step 1
def image_to_bits(image_path):
    # Load the image
    image = cv2.imread(image_path)

    # Encode the image as a byte string
    _, image_bytes = cv2.imencode('.jpeg', image)

    # Convert the byte string to a sequence of 0s and 1s
    bits = ''.join(format(byte, '08b') for byte in image_bytes.tobytes())
    return bits


def divide_bits_into_chunks(file_id, bits, chunk_size, num_of_chunks):
    packet_id = 0
    packets = []
    for i in range(math.ceil(num_of_chunks)):
        if i != math.ceil(num_of_chunks) - 1:
            packets.append(str(bin(i)[2:].zfill(16)) + str(bin(file_id)[2:].zfill(16)) + bits[0:chunk_size] + str(
                bin(0x0000)[2:].zfill(32)))
        else:
            packets.append(str(bin(i)[2:].zfill(16)) + str(bin(file_id)[2:].zfill(16)) + bits[0:chunk_size] + str(
                bin(0xFFFF)[2:].zfill(32)))
        bits = bits[chunk_size:]
    return packets


# image_path = "C:\\Users\\Doha\\Downloads\\small file.jpeg"
# image_path2 = "C:\\Users\\Doha\\Downloads\\medium file.jpeg"
# image_path3 = "C:\\Users\\Doha\\Downloads\\large file.jpeg"

image_path = "C:\\Users\\salma\\OneDrive\\Desktop\\UNI\\Spring 2024\\Network\\Project Networks CSAI 252\\images\\small-file.jpg"
image_path2 = "C:\\Users\\salma\\OneDrive\\Desktop\\UNI\\Spring 2024\\Network\\Project Networks CSAI 252\\images\\medium-file.jpg"
image_path3 = "C:\\Users\\salma\\OneDrive\\Desktop\\UNI\\Spring 2024\\Network\\Project Networks CSAI 252\\images\\large-file.jpg"

images = [image_path, image_path2, image_path3]

# open connection
s1 = s.socket(s.AF_INET, s.SOCK_DGRAM)
port = 12345
addr = ('127.0.0.1', port)

# send the 3 images
img_num = 0
retransmissions = 0
window_size = [3, 5, 7]
timeout = [0.5, 0.7, 0.9]

for j in range (3):
    for image_path in images:

        bits = image_to_bits(image_path)
        chunk_size = 1000
        file_id = 0
        num_of_chunks = len(bits) / chunk_size
        packets = divide_bits_into_chunks(file_id, bits, chunk_size, num_of_chunks)

        base = 0
        next_packet_num = 0
        # window_size = 3
        # timeout = 0.5

        def start_timer():
            return time.time()

        def end_timer(start_time):
            return time.time()

        start_time = start_timer()
        start_time2 = start_timer()
        print(f"image {img_num} with window size{window_size[j]} and time {timeout[j]}")
        print(f"Start time ", datetime.datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S.%f'))

        while base < len(packets):
            # Send all packets in the window
            while next_packet_num < base + window_size[j] and next_packet_num < len(packets):
                s1.sendto(packets[next_packet_num].encode(), addr)
                # print("Sending packet ", next_packet_num)
                next_packet_num += 1

            # Wait for acknowledgment + move window or timeout
            while True:
                try:
                    s1.settimeout(timeout[j])
                    ack, _ = s1.recvfrom(4096)
                    ack_num = int(ack.decode())
                    # print(f"Acknowledgment received for packet {ack.decode()}")

                    # Move step if received ack + Reset the timer
                    if ack_num >= base:
                        base = ack_num + 1
                        start_time = start_timer()

                    # return True unless the ack not received
                    if all(ack[base:base + window_size[j]]):
                        break

                except s.timeout:
                    # Did not receive ack -> start sending again from base
                    retransmissions += 1
                    # print("Timeout occurred, resending window")
                    next_packet_num = base
                    break

        end_time2 = end_timer(start_time)
        print(f"End time", datetime.datetime.fromtimestamp(end_time2).strftime('%Y-%m-%d %H:%M:%S.%f'))
        print(f"Elapse time", end_time2 - start_time2)
        print(f"Number of packets", num_of_chunks)
        print(f"Num of bytes of packets", chunk_size * num_of_chunks /8)
        print(f"Num of retransmissions of packets", retransmissions)
        print(f"Average transfer rateof packets", num_of_chunks / (end_time2 - start_time2 + 0.00000001), "bytes/sec")

        img_num += 1

s1.close()