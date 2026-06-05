from common import config
from common.packet import create_data_packet, parse_packet
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(2.0)  # ACK'i 2 saniye bekle

# Saglam paket gonder
paket = create_data_packet(seq_num=0, total_packets=1, payload=b"merhaba")
sock.sendto(paket, (config.SERVER_IP, config.SERVER_PORT))
print("Saglam paket gonderildi, ACK bekleniyor...")

# ACK gelmeli
try:
    data, addr = sock.recvfrom(65535)
    ack = parse_packet(data)
    print(f"ACK alindi! seq={ack['seq_num']}")
except socket.timeout:
    print("ACK gelmedi (timeout).")