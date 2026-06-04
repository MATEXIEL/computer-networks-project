"""
config.py
---------
NetProbe projesinin tum sabit ayarlari burada tutulur.
Hem istemci (client) hem sunucu (server) bu degerleri kullanir.
Tek bir yerde durmasinin sebebi: herkes ayni ayarlarla calissin,
ve deneylerde bir degeri degistirmek istedigimizde tek yeri degistirelim.
"""

# --- Ag (network) ayarlari ---
# sunucunun adresi "localhost"
SERVER_IP = "127.0.0.1"
SERVER_PORT = 9999

# --- Paket ayarlari ---
# Her veri paketinin tasiyacagi GERCEK dosya verisi miktari
PAYLOAD_SIZE = 1024

# --- Guvenilirlik ayarlari ---
# Istemci bir ACK'i ne kadar sure bekleyecek
# Bu sure dolar da ACK gelmezse paket "kayip" sayilir ve tekrar gonderilir.
# Deneylerde "timeout etkisi" senaryosu icin bu degeri degistireleckecek
TIMEOUT = 1.0

# Bir paket en fazla kac kez tekrar gonderilecek
# varsayilan 5 olmali
MAX_RETRIES = 5