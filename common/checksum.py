"""
checksum.py
-----------
Bir verinin bozulup bozulmadigini anlamak icin checksum dosyasi kullanicaz
"""

import hashlib


def calculate_checksum(data: bytes) -> bytes:
    """
    Verilen byte verisinin MD5 checksum'ini hesaplar.
    Sonuc 16 byte uzunlugunda sabit bir parmak izidir.
    """
    return hashlib.md5(data).digest()


def verify_checksum(data: bytes, received_checksum: bytes) -> bool:
    """
    Gelen verinin checksum'ini yeniden hesaplar ve
    pakette gelen checksum ile karsilastirir.
    Ayniysa True (veri saglam), farkliysa False (veri bozuk) doner.
    """
    return calculate_checksum(data) == received_checksum