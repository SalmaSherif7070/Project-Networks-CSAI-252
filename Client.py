import socket as s
from PIL import Image
import os
import random


def acknowledgement(packet):
    packet_id = packet[0:16]
    file_id = packet[16:32]
    Trailer = packet[-32:]
    return packet_id, file_id, Trailer


def extract_msg(packet):
    return packet[32:-32]

image = ''
index_of_lost_packets = [2, 208, 146, 73, 345, 249, 375, 44, 161, 368, 76, 111, 17, 162, 267, 397, 263, 181, 289, 274, 258, 248, 264, 193, 99, 94, 66, 261, 192, 175, 58, 317, 9, 204, 29, 112, 346, 207, 182, 140, 158, 235, 132, 52, 32, 239, 48, 311, 143, 116, 153, 50, 253, 3, 169, 69]# [random.randint(0, 399) for _ in range(55)]
print(index_of_lost_packets)
pos_ack = -1

s2 = s.socket(s.AF_INET, s.SOCK_DGRAM)
port = 12345
address = ('127.0.0.1', port)
s2.bind(address)

expected_packet_num = 0

while True:
    data, server = s2.recvfrom(4096)
    packet_id, file_id, Trailer = acknowledgement(data.decode())
    packet_id = int(packet_id, 2)
    if packet_id in index_of_lost_packets:
        # print("fffffff",packet_id)
        index_of_lost_packets.remove(int(packet_id))
        packet_id = int(packet_id) + 1
        

    print('P_ID ', packet_id, "expected_packet_num ", expected_packet_num)

    if packet_id == expected_packet_num:
        print(f'Packet {expected_packet_num} received correctly')
        pos_ack = expected_packet_num
        expected_packet_num += 1
        print(Trailer)
        image = image + extract_msg(data.decode())
    else:
        print(f'Packet {packet_id} received out of order')

    # Send acknowledgment for the last correctly received packet
    ack_message = f"{pos_ack}"
    s2.sendto(ack_message.encode(), server)

    if Trailer == '00000000000000001111111111111111':
        print(image)
        print(f'Last packet received: {data.decode()}')
        break


# print(image)
def bits_to_image(bits, width, height):
    img = Image.new('1', (width, height))
    pixels = img.load()
    idx = 0
    for y in range(height):
        for x in range(width):
            pixels[x, y] = int(bits[idx]) * 255
            idx += 1
    return img


width = 800
height = 500
img = bits_to_image(image, width, height)
# img.show()
img.save('Res_images\output.png')
os.system('start output.png')

s2.close()
