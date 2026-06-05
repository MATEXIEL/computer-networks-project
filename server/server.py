"""
server.py
---------
NetProbe sunucusu 
sadece UDP soketini acip gelen paketleri dinler.
gelen paketi acip (parse_packet) icindekileri okur ve
checksum dogru mu kontrol eder

"""

import socket
from common import config
from common.packet import parse_packet, create_ack_packet, TYPE_DATA
 
 
def start_server():
    # UDP soketi olustur
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((config.SERVER_IP, config.SERVER_PORT))
 
    # 1 saniyelik timeout: soket her saniye "uyanir", boylece Ctrl+C
    # bekleme sirasinda da yakalanabilir (Windows'ta takilmayi onler).
    sock.settimeout(1.0)
 
    print(f"[SUNUCU] Dinlemede: {config.SERVER_IP}:{config.SERVER_PORT}")
    print("[SUNUCU] Paket bekleniyor... (durdurmak icin Ctrl+C)")

    
 
    while True:
        try:
            data, addr = sock.recvfrom(65535)
        except socket.timeout:
            # Bu saniye icinde paket gelmedi; donguyu basa al, Ctrl+C kontrol edilsin.
            continue
 
        # Gelen ham byte'i acip okunabilir hale getir
        pkt = parse_packet(data)
 
        # Veri paketi mi, ACK mi? (su an sadece veri bekliyoruz)
        if pkt["type"] == TYPE_DATA:
            if pkt["is_valid"]:
                # Checksum tuttu -> veri saglam
                print(f"[SUNUCU] SAGLAM paket alindi | seq={pkt['seq_num']} "
                      f"| toplam={pkt['total_packets']} "
                      f"| veri='{pkt['payload'].decode(errors='replace')}'")
                # ACK uret ve paketi gonderen adrese (addr) geri yolla
                ack = create_ack_packet(pkt["seq_num"])
                sock.sendto(ack, addr)
                print(f"[SUNUCU] ACK gonderildi | seq={pkt['seq_num']}")
            else:
                # Checksum tutmadi -> veri bozuk, paketi atiyoruz (ACK de gondermeyecegiz)
                print(f"[SUNUCU] BOZUK paket atildi | seq={pkt['seq_num']}")
        else:
            print(f"[SUNUCU] Beklenmeyen paket tipi: {pkt['type']}")
 
 
if __name__ == "__main__":
    try:
        start_server()
    except KeyboardInterrupt:
        print("\n[SUNUCU] Kapatildi.")