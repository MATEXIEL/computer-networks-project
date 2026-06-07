# UDP Üzerinde Güvenilir Veri Aktarımı (Stop-and-Wait ARQ)

Bu proje, güvensiz bir taşıma katmanı protokolü olan UDP üzerinde, uygulama katmanında çeşitli hata kontrol mekanizmaları kurarak güvenilir bir dosya transfer sistemi (Reliable Data Transfer) sağlamayı amaçlamaktadır. 

## Proje Ekibi (Grup 02)
* İstemci ve Hata Yönetimi: Muhammed Ali TOPRAK
* Sunucu ve Veri Bütünlüğü: Fuat ÜZÜLMEZ
* Ağ Analizi ve Görselleştirme: Furkan BULDUKLU

## Sistem Özellikleri
* Protokol: Stop-and-Wait ARQ
* Bütünlük Kontrolü: MD5 Checksum
* Hata Toleransı: Dinamik Timeout ve Maksimum Retransmission (5 deneme) yönetimi.
* Analiz: Farklı paket boyutları, kayıp oranları ve zaman aşımı süreleri altında Throughput/Goodput analizi.

## Nasıl Çalıştırılır?
Sistemi uçtan uca test etmek için iki ayrı terminal penceresi açılmalıdır.

1. Sunucuyu Başlatmak:
python -m server.server

2. İstemciyi Başlatmak (Dosya Aktarımı):
python -m client.client

3. Analiz ve Grafikleri Üretmek (Aktarım Bittikten Sonra):
python -m analysis.visualizer
