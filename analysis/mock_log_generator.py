import csv
import random
import time

def generate_mock_logs(filename, total_packets):
    # Föydeki loglama gereksinimlerine göre sütunlar
    headers = ['packet_seq', 'send_time', 'ack_time', 'is_timeout', 'retransmission_count', 'status']
    
    start_time = time.time()
    
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(headers) # Başlıkları yazdırıyoruz
        
        current_time = start_time
        
        for seq in range(total_packets):
            # Ortalama RTT (Gecikme) simülasyonu
            rtt = random.uniform(0.01, 0.05) 
            send_time = current_time
            
            # %15 ihtimalle paket kaybolsun, timeout ve retransmission yaşansın
            if random.random() < 0.15:
                is_timeout = 1
                retransmissions = random.randint(1, 4)
                ack_time = send_time + (0.5 * is_timeout) + rtt # 0.5 sn timeout süresi eklendi
                status = 'Success'
                
                # Föye göre maksimum 5 denemede de başarısız olma durumu
                if random.random() < 0.05:
                    retransmissions = 5
                    ack_time = -1 # Paket ulaştırılamadı
                    status = 'Failed'
            else:
                # Sorunsuz giden paketler
                is_timeout = 0
                retransmissions = 0
                ack_time = send_time + rtt
                status = 'Success'
                
            writer.writerow([seq, send_time, ack_time, is_timeout, retransmissions, status])
            current_time = send_time + 0.002 # Bir sonraki paketin gönderim süresi

    print(f"[{filename}] başarıyla oluşturuldu! İçinde analiz yapabileceğimiz {total_packets} adet sahte paket logu var.")

if __name__ == "__main__":
    # Test için 1000 paketlik sahte bir log dosyası üretiyoruz
    generate_mock_logs("transfer_logs.csv", 1000)