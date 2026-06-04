"""
server.py
---------
NetProbe sunucusu 
sadece UDP soketini acip gelen paketleri dinler.

"""

import socket
from common import config


def start_server():
    # 1) UDP soketi olustur.
    #    AF_INET = IPv4 adres ailesi
    #    SOCK_DGRAM = UDP (TCP olsaydi SOCK_STREAM olurdu)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # 2) Soketi adrese BAGLA (bind): "ben bu IP ve port'u dinliyorum" de.
    #    config.py'den geliyor: 127.0.0.1 ve 9999
    sock.bind((config.SERVER_IP, config.SERVER_PORT))

    print(f"[SUNUCU] Dinlemede: {config.SERVER_IP}:{config.SERVER_PORT}")
    print("[SUNUCU] Paket bekleniyor... (durdurmak icin Ctrl+C)")

    # 3) Sonsuz dongu: gelen paketleri bekle.
    while True:
        # recvfrom: bir paket gelene kadar bekler.
        #   data    = gelen ham byte verisi
        #   addr    = paketi gonderen istemcinin adresi (IP, port)
        # Parametre 65535 = bir seferde alinabilecek maksimum byte.
        data, addr = sock.recvfrom(65535)
        print(f"[SUNUCU] {addr} adresinden {len(data)} byte geldi.")


if __name__ == "__main__":
    # Ctrl+C ile temiz cikis icin try/except
    try:
        start_server()
    except KeyboardInterrupt:
        print("\n[SUNUCU] Kapatildi.")