import socket as s
from PIL import Image
import os
import random
import matplotlib.pyplot as plt
import time
import datetime
import copy 
import cv2
import numpy as np


def acknowledgement(packet):
    packet_id = packet[0:16]
    file_id = packet[16:32]
    Trailer = packet[-32:]
    return packet_id, file_id, Trailer

def extract_msg(packet):
    return packet[32:-32]

def bits_to_image(bits, width, height):
    bytes_array = bytearray(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))
    nparr = np.frombuffer(bytes_array, dtype=np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR).reshape(height, width, 3)
    return image


# def start_timer():
#         return time.time()

image = ''

pos_ack = -1

s2 = s.socket(s.AF_INET, s.SOCK_DGRAM)
port = 12345
address = ('127.0.0.1', port)
s2.bind(address)
img_dim = [(800,500), (1280,720), (1280,853), (800,500), (1280,720), (1280,853), (800,500), (1280,720), (1280,853)]

for i in range (9):
    index_of_lost_packets = [random.randint(0, 399) for _ in range(55)]
    copy_of_index_of_lost_packets = copy.deepcopy(index_of_lost_packets)
    
    expected_packet_num = 0
    list_of_times = []
    list_of_ids = []
    list_of_colors = []
    # client_timer = start_timer()

    while True:
        data, server = s2.recvfrom(4096)
        packet_id, file_id, Trailer = acknowledgement(data.decode())
        packet_id = int(packet_id, 2)
        if packet_id in index_of_lost_packets:
            index_of_lost_packets.remove(int(packet_id))
            packet_id = int(packet_id) + 1
            

        # print('P_ID ', packet_id, "expected_packet_num ", expected_packet_num)

        if packet_id == expected_packet_num:
            # print(f'Packet {expected_packet_num} received correctly')
            pos_ack = expected_packet_num
            expected_packet_num += 1
            # print(Trailer)
            image = image + extract_msg(data.decode())
            current_time = datetime.datetime.now()
            formatted_time = current_time.strftime("%H:%M:%S")
            milliseconds_since_epoch = current_time.timestamp() * 1000
            
            if (int(packet_id) in copy_of_index_of_lost_packets ):
            
                list_of_colors.append('red')
            else:
                list_of_colors.append('blue')
            
            list_of_times.append(milliseconds_since_epoch)
            list_of_ids.append(packet_id)
        # else:
        #     print(f'Packet {packet_id} received out of order')

        # Send acknowledgment for the last correctly received packet
        ack_message = f"{pos_ack}"
        s2.sendto(ack_message.encode(), server)

        if Trailer == '00000000000000001111111111111111':
            # print(image)
            # print(f'Last packet received: {data.decode()}')
            break

    plt.figure(figsize=(10, 6))
    for time, color, number in zip(list_of_times, list_of_colors, list_of_ids):
        plt.scatter(time, number, color=color)

    plt.xlabel('Time')
    plt.ylabel('Number')
    plt.title(f'Scatter Plot of Time vs Number with Color Coding{i}')
    plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    print("plt.show() ", i)
    width = img_dim[i][0]
    height = img_dim[i][1]
    img = bits_to_image(image, width, height)
    output_filename = f'output_image{i}.png'
    cv2.imwrite(output_filename, img)


    image = ''

s2.close()