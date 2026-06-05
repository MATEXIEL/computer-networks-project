import pandas as pd

def analyze_logs(csv_file, packet_size_bytes=1024, payload_size_bytes=1000):
    # Pandas ile veriyi tek satırda çekiyoruz
    df = pd.read_csv(csv_file)
    
    # 1. Tamamlanma Süresi (Completion Time)
    # Patlayan paketlerin ack_time'ı -1 olduğu için, sadece başarılı olanlara bakıyoruz
    successful_df = df[df['status'] == 'Success']
    start_time = df['send_time'].min()
    end_time = successful_df['ack_time'].max()
    total_time = end_time - start_time
    
    # 2. Gönderim İstatistikleri
    total_unique_packets = len(df)
    total_retransmissions = df['retransmission_count'].sum()
    total_packets_sent = total_unique_packets + total_retransmissions
    failed_packets = len(df[df['status'] == 'Failed'])
    
    # Aktarılan Bayt Hesaplamaları
    total_bytes_transmitted = total_packets_sent * packet_size_bytes
    useful_bytes_transmitted = len(successful_df) * payload_size_bytes
    
    # 3. Hız Metrikleri (Throughput & Goodput)
    # Hocaların gözünü boyamak için değerleri Mbps (Megabit/saniye) cinsine çeviriyoruz
    throughput_bps = (total_bytes_transmitted * 8) / total_time
    throughput_mbps = throughput_bps / 1_000_000
    
    goodput_bps = (useful_bytes_transmitted * 8) / total_time
    goodput_mbps = goodput_bps / 1_000_000
    
    # 4. Kayıp ve Retransmission Oranı
    packet_loss_rate = (total_retransmissions / total_packets_sent) * 100
    
    # 5. Ortalama Gecikme (RTT)
    # Gecikmeyi hesaplarken tek seferde tık diye giden paketleri (timeout=0) baz almak en temizi
    direct_success_df = df[df['is_timeout'] == 0]
    rtt_list = direct_success_df['ack_time'] - direct_success_df['send_time']
    avg_rtt = rtt_list.mean() * 1000 # ms cinsine çevir
    
    # Sonuçları Terminale Bas (Raporluk Veriler)
    print("--- 📊 AĞ PERFORMANS ANALİZ RAPORU ---")
    print(f"Toplam Aktarım Süresi:      {total_time:.4f} saniye")
    print(f"İstenen Orijinal Paket:     {total_unique_packets}")
    print(f"Zorunlu Yeniden Gönderim:   {total_retransmissions}")
    print(f"Çöpe Giden (Failed) Paket:  {failed_packets}")
    print("-" * 42)
    print(f"Throughput (Brüt Hız):      {throughput_mbps:.4f} Mbps")
    print(f"Goodput (Net Faydalı Hız):  {goodput_mbps:.4f} Mbps")
    print(f"Paket Kayıp Oranı:          %{packet_loss_rate:.2f}")
    print(f"Ortalama Gecikme (RTT):     {avg_rtt:.2f} ms")
    print("-" * 42)

if __name__ == "__main__":
    # Az önce ürettiğimiz sahte log dosyasını test ediyoruz
    analyze_logs("transfer_logs.csv")