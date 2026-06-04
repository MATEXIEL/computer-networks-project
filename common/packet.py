"""
Ag uzerinden sadece byte gonderebilir bu pakette birden cok bilgi
tasimak istiyoruz (tip, sira no, toplam, checksum, veri).
Bu dosya, pack ve unpack islemlerini yapar

Paket yapisi
  [ HEADER (sabit boyut) ] + [ PAYLOAD (asil veri) ]

Header alanlari:
  - packet_type   : 0 = veri paketi, 1 = ACK paketi
  - seq_num       : sira numarasi
  - total_packets : dosya toplam kac parcaya bolundu
  - checksum      : payload'in 16 byte'lik parmak izi
"""

import struct
from common.checksum import calculate_checksum, verify_checksum

# Paket tipleri
TYPE_DATA = 0   # veri paketi
TYPE_ACK = 1    # onay (acknowledgement) paketi

# Header formati (struct icin):
#   B = 1 byte'lik sayi (packet_type icin)
#   I = 4 byte'lik sayi (seq_num ve total_packets icin)
#   16s = 16 byte'lik dizi (checksum icin)
# "!" = network byte order (ag standardi sira)
HEADER_FORMAT = "!BII16s"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)  # bu formatin kac byte tuttugu


def create_data_packet(seq_num: int, total_packets: int, payload: bytes) -> bytes:
    """
    Bir VERI paketi olusturur ve gondermeye hazir byte dizisi dondurur.
    Checksum, payload'dan otomatik hesaplanir.
    """
    checksum = calculate_checksum(payload)
    header = struct.pack(HEADER_FORMAT, TYPE_DATA, seq_num, total_packets, checksum)
    return header + payload


def create_ack_packet(seq_num: int) -> bytes:
    """
    Bir ACK paketi olusturur. ACK'in payload'i yoktur,
    sadece "hangi sira numarasini onayliyorum" bilgisini tasir.
    Checksum alani bos (16 sifir byte) birakilir.
    """
    empty_checksum = b"\x00" * 16
    header = struct.pack(HEADER_FORMAT, TYPE_ACK, seq_num, 0, empty_checksum)
    return header


def parse_packet(raw_data: bytes) -> dict:
    """
    Gelen ham byte dizisini ACAR ve okunabilir bir sozluk dondurur.
    Donen sozluk:
      - type          : TYPE_DATA veya TYPE_ACK
      - seq_num        : sira numarasi
      - total_packets  : toplam paket sayisi
      - payload        : asil veri (ACK'te bos)
      - is_valid       : checksum dogru mu? (veri paketi icin anlamli)
    """
    # Once header'i ayir, gerisi payload
    header = raw_data[:HEADER_SIZE]
    payload = raw_data[HEADER_SIZE:]

    packet_type, seq_num, total_packets, checksum = struct.unpack(HEADER_FORMAT, header)

    # Veri paketiyse checksum'i dogrula; ACK ise bu kontrol gereksiz
    if packet_type == TYPE_DATA:
        is_valid = verify_checksum(payload, checksum)
    else:
        is_valid = True

    return {
        "type": packet_type,
        "seq_num": seq_num,
        "total_packets": total_packets,
        "payload": payload,
        "is_valid": is_valid,
    }