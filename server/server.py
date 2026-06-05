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

       # Daha once alinan sira numaralarini burada tutulur duplicate kontrol yapmak icin
    alinan_seqler = set() 
 
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
                seq = pkt["seq_num"]

                if seq in alinan_seqler:
                    # DUPLICATE: bu paketi daha once aldik.
                    # Veriyi TEKRAR KAYDETMEYECEGIZ, ama ACK'i yine de gondeririz
                    # (cunku istemcinin onceki ACK'i kaybolmus olabilir).
                    print(f"[SUNUCU] DUPLICATE paket (yok sayildi) | seq={seq}")
                else:
                    # ILK KEZ gelen saglam paket
                    alinan_seqler.add(seq)
                    print(f"[SUNUCU] YENI paket alindi | seq={seq} "
                          f"| toplam={pkt['total_packets']} "
                          f"| veri='{pkt['payload'].decode(errors='replace')}'")

                # Duplicate de olsa, yeni de olsa: HER ZAMAN ACK gonder
                ack = create_ack_packet(seq)
                sock.sendto(ack, addr)
                print(f"[SUNUCU] ACK gonderildi | seq={seq}")
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