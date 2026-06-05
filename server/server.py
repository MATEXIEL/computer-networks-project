"""
server.py
---------
NetProbe sunucusu (alici taraf).

yapay paket kaybi simulasyonu ekledim.
Gelen paketlerin belli bir orani (LOSS_RATE) rastgele "kayip" sayilir;
o paket islenmez ve ACK gonderilmez. Boylece istemcinin timeout +
retransmission mekanizmasi gercek kayip kosulunda test edilebilir.
"""

import socket
import hashlib
import random
from common import config
from common.packet import parse_packet, create_ack_packet, TYPE_DATA

# Birlestirilen dosyanin kaydedilecegi yer
OUTPUT_FILE = "alinan_dosya.dat"

# Yapay paket kaybi orani (0.0 = kayip yok, 0.2 = gelen paketlerin %20'si dusurulur)
# Deneylerde "kayip oraninin etkisi" senaryosu icin bu degeri degistirecegiz.
LOSS_RATE = 0.0


def start_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((config.SERVER_IP, config.SERVER_PORT))
    sock.settimeout(1.0)

    print(f"[SUNUCU] Dinlemede: {config.SERVER_IP}:{config.SERVER_PORT}")
    print(f"[SUNUCU] Yapay kayip orani: %{int(LOSS_RATE * 100)}")
    print("[SUNUCU] Paket bekleniyor... (durdurmak icin Ctrl+C)")

    alinan_parcalar = {}
    toplam_paket = None

    while True:
        try:
            data, addr = sock.recvfrom(65535)
        except socket.timeout:
            continue

        # --- YAPAY PAKET KAYBI ---
        # Rastgele bir sayi cek; kayip oraninin altindaysa paketi DUSUR.
        # Islemeyiz, ACK de gondermeyiz -> istemci timeout'a duser, tekrar gonderir.
        if random.random() < LOSS_RATE:
            pkt_kayip = parse_packet(data)
            print(f"[SUNUCU] >>> PAKET DUSURULDU (yapay kayip) | seq={pkt_kayip['seq_num']}")
            continue

        pkt = parse_packet(data)

        if pkt["type"] == TYPE_DATA:
            if pkt["is_valid"]:
                seq = pkt["seq_num"]
                toplam_paket = pkt["total_packets"]

                if seq in alinan_parcalar:
                    print(f"[SUNUCU] DUPLICATE paket (yok sayildi) | seq={seq}")
                else:
                    alinan_parcalar[seq] = pkt["payload"]
                    print(f"[SUNUCU] YENI paket alindi | seq={seq} "
                          f"| toplam={toplam_paket} "
                          f"| ({len(alinan_parcalar)}/{toplam_paket} parca)")

                # Her durumda ACK gonder
                ack = create_ack_packet(seq)
                sock.sendto(ack, addr)

                # Butun parcalar geldi mi?
                if len(alinan_parcalar) == toplam_paket:
                    dosyayi_birlestir(alinan_parcalar, toplam_paket)
                    alinan_parcalar = {}
                    toplam_paket = None
            else:
                print(f"[SUNUCU] BOZUK paket atildi (ACK yok) | seq={pkt['seq_num']}")
        else:
            print(f"[SUNUCU] Beklenmeyen paket tipi: {pkt['type']}")


def dosyayi_birlestir(parcalar: dict, toplam: int):
    """Toplanan parcalari seq sirasina gore birlestirir, diske yazar ve hash'ini gosterir."""
    butun_veri = b""
    for seq in range(toplam):
        butun_veri += parcalar[seq]

    with open(OUTPUT_FILE, "wb") as f:
        f.write(butun_veri)

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