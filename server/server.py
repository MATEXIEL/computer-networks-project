import socket
import hashlib
import random
import sys
from common import config
from common.packet import parse_packet, create_ack_packet, TYPE_DATA

OUTPUT_FILE = "alinan_dosya.dat"
LOSS_RATE = 0.0

def start_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((config.SERVER_IP, config.SERVER_PORT))
    sock.settimeout(1.0)

    print(f"[SUNUCU] Dinlemede: {config.SERVER_IP}:{config.SERVER_PORT}")
    print(f"[SUNUCU] Yapay kayip orani: %{int(LOSS_RATE * 100)}")

    alinan_parcalar = {}
    toplam_paket = None

    while True:
        try:
            data, addr = sock.recvfrom(65535)
        except socket.timeout:
            continue

        if random.random() < LOSS_RATE:
            continue 

        pkt = parse_packet(data)

        if pkt["type"] == TYPE_DATA:
            if pkt["is_valid"]:
                seq = pkt["seq_num"]
                toplam_paket = pkt["total_packets"]

                if seq not in alinan_parcalar:
                    alinan_parcalar[seq] = pkt["payload"]

                ack = create_ack_packet(seq)
                sock.sendto(ack, addr)

                if len(alinan_parcalar) == toplam_paket:
                    dosyayi_birlestir(alinan_parcalar, toplam_paket)
                    alinan_parcalar = {}
                    toplam_paket = None

def dosyayi_birlestir(parcalar: dict, toplam: int):
    butun_veri = b""
    for seq in range(toplam):
        butun_veri += parcalar[seq]

    with open(OUTPUT_FILE, "wb") as f:
        f.write(butun_veri)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            LOSS_RATE = float(sys.argv[1])
        except ValueError:
            pass
            
    try:
        start_server()
    except KeyboardInterrupt:
        print("\n[SUNUCU] Kapatildi.")
