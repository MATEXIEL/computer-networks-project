"""
server.py
---------
NetProbe sunucusu (alici taraf).

ASAMA 5: gelen paketleri biriktirir, hepsi gelince dosyayi birlestirip
diske yazar ve butunlugunu (hash) dogrular.
"""

import socket
import hashlib
from common import config
from common.packet import parse_packet, create_ack_packet, TYPE_DATA

# Birlestirilen dosyanin kaydedilecegi yer
OUTPUT_FILE = "alinan_dosya.dat"


def start_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((config.SERVER_IP, config.SERVER_PORT))
    sock.settimeout(1.0)

    print(f"[SUNUCU] Dinlemede: {config.SERVER_IP}:{config.SERVER_PORT}")
    print("[SUNUCU] Paket bekleniyor... (durdurmak icin Ctrl+C)")

    # seq -> payload eslesmesi. UDP'de paketler sirasiz gelebilir,
    # bu yuzden seq ile saklayip sonunda siraya diziyoruz.
    alinan_parcalar = {}
    toplam_paket = None  # ilk paketten ogrenecegiz

    while True:
        try:
            data, addr = sock.recvfrom(65535)
        except socket.timeout:
            continue

        pkt = parse_packet(data)

        if pkt["type"] == TYPE_DATA:
            if pkt["is_valid"]:
                seq = pkt["seq_num"]
                toplam_paket = pkt["total_packets"]

                if seq in alinan_parcalar:
                    # DUPLICATE: veriyi tekrar kaydetme, ama ACK yine gonder
                    print(f"[SUNUCU] DUPLICATE paket (yok sayildi) | seq={seq}")
                else:
                    # ILK KEZ gelen parca: payload'i sakla
                    alinan_parcalar[seq] = pkt["payload"]
                    print(f"[SUNUCU] YENI paket alindi | seq={seq} "
                          f"| toplam={toplam_paket} "
                          f"| ({len(alinan_parcalar)}/{toplam_paket} parca)")

                # Her durumda ACK gonder
                ack = create_ack_packet(seq)
                sock.sendto(ack, addr)

                # Butun parcalar geldi mi? Geldiyse dosyayi birlestir.
                if len(alinan_parcalar) == toplam_paket:
                    dosyayi_birlestir(alinan_parcalar, toplam_paket)
                    # Yeni bir aktarim icin durumu sifirla
                    alinan_parcalar = {}
                    toplam_paket = None
            else:
                print(f"[SUNUCU] BOZUK paket atildi (ACK yok) | seq={pkt['seq_num']}")
        else:
            print(f"[SUNUCU] Beklenmeyen paket tipi: {pkt['type']}")


def dosyayi_birlestir(parcalar: dict, toplam: int):
    """Toplanan parcalari seq sirasina gore birlestirir, diske yazar ve hash'ini gosterir."""
    # 0'dan toplam-1'e kadar siraya dizip birlestir
    butun_veri = b""
    for seq in range(toplam):
        butun_veri += parcalar[seq]

    # Diske yaz
    with open(OUTPUT_FILE, "wb") as f:
        f.write(butun_veri)

    # Butunluk kaniti: alinan dosyanin hash'i
    dosya_hash = hashlib.md5(butun_veri).hexdigest()

    print("\n[SUNUCU] ===== DOSYA TAMAMLANDI =====")
    print(f"[SUNUCU] Kaydedildi: {OUTPUT_FILE} ({len(butun_veri)} byte)")
    print(f"[SUNUCU] MD5 hash: {dosya_hash}")
    print("[SUNUCU] (Bu hash istemcideki orijinal dosyanin hash'i ile ayni olmali)\n")


if __name__ == "__main__":
    try:
        start_server()
    except KeyboardInterrupt:
        print("\n[SUNUCU] Kapatildi.")