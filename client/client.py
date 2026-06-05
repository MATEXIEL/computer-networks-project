import socket
import os
import math
import time
import csv

# common modullerinden importlar yapiliyor
from common.config import SERVER_IP, SERVER_PORT, PAYLOAD_SIZE, TIMEOUT, MAX_RETRIES
from common.packet import create_data_packet, parse_packet, TYPE_ACK

def send_file(file_path):
    if not os.path.exists(file_path):
        print(f"[!] Hata: '{file_path}' bulunamadi.")
        return

    # UDP soketinin olusturulmasi ve timeout ayari
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(TIMEOUT)
    server_address = (SERVER_IP, SERVER_PORT)

    file_size = os.path.getsize(file_path)
    total_packets = math.ceil(file_size / PAYLOAD_SIZE)
    
    print(f"[*] Aktarim basliyor: {file_path} ({file_size} bytes)")
    
    # Furkan'in formatina uygun CSV dosyasini hazirliyoruz
    log_filename = "transfer_logs.csv"
    headers = ['packet_seq', 'send_time', 'ack_time', 'is_timeout', 'retransmission_count', 'status']
    
    with open(file_path, 'rb') as f, open(log_filename, mode='w', newline='', encoding='utf-8') as log_file:
        log_writer = csv.writer(log_file)
        log_writer.writerow(headers) # Furkan'in istedigi basliklari yaziyoruz

        for seq_num in range(total_packets):
            chunk = f.read(PAYLOAD_SIZE)
            packet = create_data_packet(seq_num, total_packets, chunk)
            
            retries = 0
            ack_received = False
            is_timeout_flag = 0
            
            # Gonderim baslangic zamani (Furkan'in logu icin)
            send_time = time.time()
            ack_time = -1
            status = 'Failed'
            
            # Stop-and-Wait ve Retransmission Dongusu
            while retries < MAX_RETRIES and not ack_received:
                try:
                    print(f"[*] Gonderiliyor: Seq={seq_num}/{total_packets-1} (Deneme: {retries+1}/{MAX_RETRIES})")
                    client_socket.sendto(packet, server_address)
                    
                    ack_data, _ = client_socket.recvfrom(1024)
                    ack_info = parse_packet(ack_data)
                    
                    if ack_info["type"] == TYPE_ACK and ack_info["seq_num"] == seq_num:
                        ack_time = time.time()
                        status = 'Success'
                        ack_received = True
                        print(f"[+] Basarili: ACK {seq_num} alindi.\n")
                        
                except (socket.timeout, ConnectionResetError):
                    print(f"[-] Timeout veya Baglanti Reddi! Paket {seq_num} ulasmadi.")
                    is_timeout_flag = 1
                    retries += 1
                    time.sleep(0.5) # Hata aninda programin cok hizli spam yapmasini engeller
            
            # Paketin log satirini CSV'ye yaziyoruz (Furkan'in analiz motoru icin)
            log_writer.writerow([seq_num, send_time, ack_time, is_timeout_flag, retries, status])
            
            if not ack_received:
                print(f"[!] HATA: Paket {seq_num}, {MAX_RETRIES} kez gonderilmesine ragmen ulasmadi.")
                print("[-] Aktarim iptal ediliyor.")
                client_socket.close()
                return

    print(f"[*] Aktarim tamamlandi! Loglar '{log_filename}' dosyasina kaydedildi.")
    client_socket.close()

if __name__ == "__main__":
    # Test icin kucuk bir dosya olusturdum
    test_file_name = "test.txt"
    with open(test_file_name, "w") as temp_file:
        temp_file.write("BTU Ag Projesi Test " * 50)
        
    send_file(test_file_name)