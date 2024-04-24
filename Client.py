import socket as s


def acknowledgement(packet):
    packet_id = packet[0:16]
    file_id = packet[16:32]
    # message = packet[32:-32]
    # Trailer = packet[-32:]
    return packet_id + file_id



s2 = s.socket(s.AF_INET, s.SOCK_DGRAM)
port = 12345
address = ('127.0.0.1', port)


# acknowledgement = acknowledgement(data.decode()).encode()
sent = s2.sendto(b"Hello", address)

data, server = s2.recvfrom(4096)

print(f'received {data.decode()}')
s2.close()
