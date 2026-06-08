import socket
import os
import math
import time
import csv
import argparse

from common.config import SERVER_IP, SERVER_PORT, MAX_RETRIES
from common.packet import create_data_packet, parse_packet, TYPE_ACK

def send_file(file_path, payload_size, timeout_val, log_filename):
    if not os.path.exists(file_path):
        print(f"[!] Hata: '{file_path}' bulunamadi.")
        return

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(timeout_val)
    server_address = (SERVER_IP, SERVER_PORT)

    file_size = os.path.getsize(file_path)
    total_packets = math.ceil(file_size / payload_size)
    
    print(f"[*] Aktarim basliyor: {file_path} ({file_size} bytes, Paket Boyutu: {payload_size}B)")
    
    headers = ['packet_seq', 'send_time', 'ack_time', 'is_timeout', 'retransmission_count', 'status']
    
    with open(file_path, 'rb') as f, open(log_filename, mode='w', newline='', encoding='utf-8') as log_file:
        log_writer = csv.writer(log_file)
        log_writer.writerow(headers)

        for seq_num in range(total_packets):
            chunk = f.read(payload_size)
            packet = create_data_packet(seq_num, total_packets, chunk)
            
            retries = 0
            ack_received = False
            is_timeout_flag = 0
            
            send_time = time.time()
            ack_time = -1
            status = 'Failed'
            
            while retries < MAX_RETRIES and not ack_received:
                try:
                    client_socket.sendto(packet, server_address)
                    ack_data, _ = client_socket.recvfrom(1024)
                    ack_info = parse_packet(ack_data)
                    
                    if ack_info["type"] == TYPE_ACK and ack_info["seq_num"] == seq_num:
                        ack_time = time.time()
                        status = 'Success'
                        ack_received = True
                        
                except (socket.timeout, ConnectionResetError):
                    is_timeout_flag = 1
                    retries += 1
                    time.sleep(0.01)
            
            log_writer.writerow([seq_num, send_time, ack_time, is_timeout_flag, retries, status])
            
            if not ack_received:
                print(f"[!] HATA: Paket {seq_num}, {MAX_RETRIES} kez gonderilmesine ragmen ulasmadi.")
                print("[-] Aktarim iptal ediliyor.")
                client_socket.close()
                return

    print(f"[*] Aktarim tamamlandi! Loglar '{log_filename}' dosyasina kaydedildi.")
    client_socket.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default="test.txt")
    parser.add_argument("--payload", type=int, default=1024)
    parser.add_argument("--timeout", type=float, default=1.0)
    parser.add_argument("--log", default="transfer_logs.csv")
    args = parser.parse_args()

    if not os.path.exists(args.file):
        with open(args.file, "w") as temp_file:
            temp_file.write("BTU Ag Projesi Test " * 50)
            
    send_file(args.file, args.payload, args.timeout, args.log)
