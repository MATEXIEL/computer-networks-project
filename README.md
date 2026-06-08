GitHub Repo Linki: https://github.com/MATEXIEL/computer-networks-project

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

Sistemi test etmek ve aktarım metriklerini gözlemlemek için:

### Tam Otomatik Deney Senaryoları
Proje föyünde istenen tüm senaryoları (farklı paket boyutları, timeout değerleri, yapay kayıp oranları ve dosya boyutları) gerçek zamanlı soketler üzerinden otomatik olarak koşturmak ve analiz grafiklerini üretmek için tek bir komut yeterlidir:

```bash
python -m analysis.visualizer
```
(Not: Bu otomasyon betiği; sunucu ve istemci süreçlerini arka planda sırasıyla kendisi başlatır, ağ testlerini fiziksel olarak yapar ve işi bitince süreçleri güvenlice kapatır. Üretilen performans grafikleri graphs/ klasörüne kaydedilir.)
