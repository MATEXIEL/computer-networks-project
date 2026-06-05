"""
visualizer.py
=============
NetProbe Projesi - Deney Otomasyonu ve Görselleştirme Modülü
Kişi 3: Loglama, Analiz ve Deneyler

Bu betik 4 farklı senaryoyu simüle eder, analiz eder ve
karşılaştırmalı grafikleri PNG olarak kaydeder.

Kullanım:
    python visualizer.py

Çıktılar (graphs/ klasörüne kaydedilir):
    senaryo1_paket_boyutu.png
    senaryo2_timeout.png
    senaryo3_kayip_orani.png
    senaryo4_dosya_boyutu.png
"""

import os
import csv
import random
import time
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# ─────────────────────────────────────────────
#  AYARLAR
# ─────────────────────────────────────────────
OUTPUT_DIR = "graphs"           # PNG'ler buraya kaydedilir
TEMP_LOG   = "temp_scenario.csv"  # Her senaryo bu geçici dosyayı kullanır

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Grafik genel stili
plt.rcParams.update({
    "figure.facecolor": "#1e1e2e",
    "axes.facecolor":   "#2a2a3e",
    "axes.edgecolor":   "#555577",
    "axes.labelcolor":  "#cdd6f4",
    "xtick.color":      "#cdd6f4",
    "ytick.color":      "#cdd6f4",
    "text.color":       "#cdd6f4",
    "grid.color":       "#3a3a5a",
    "grid.linestyle":   "--",
    "grid.alpha":       0.5,
    "font.family":      "monospace",
    "font.size":        10,
    "axes.titlesize":   12,
    "axes.titleweight": "bold",
})

COLORS = ["#89b4fa", "#a6e3a1", "#fab387", "#f38ba8", "#cba6f7"]


# ─────────────────────────────────────────────
#  YARDIMCI: LOG ÜRET
# ─────────────────────────────────────────────
def generate_log(filename, total_packets, loss_rate=0.15,
                 timeout_sec=0.5, rtt_min=0.01, rtt_max=0.05):
    """
    mock_log_generator.py mantığının parametrize edilmiş versiyonu.
    Her senaryo bu fonksiyonu farklı parametrelerle çağırır.
    """
    headers = ["packet_seq", "send_time", "ack_time",
               "is_timeout", "retransmission_count", "status"]
    start_time = time.time()
    current_time = start_time

    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)

        for seq in range(total_packets):
            rtt = random.uniform(rtt_min, rtt_max)
            send_time = current_time

            if random.random() < loss_rate:
                is_timeout = 1
                retransmissions = random.randint(1, 4)
                ack_time = send_time + timeout_sec + rtt

                # Maksimum 5 denemede de başarısız olma
                if random.random() < 0.05:
                    retransmissions = 5
                    ack_time = -1
                    status = "Failed"
                else:
                    status = "Success"
            else:
                is_timeout = 0
                retransmissions = 0
                ack_time = send_time + rtt
                status = "Success"

            writer.writerow([seq, send_time, ack_time,
                              is_timeout, retransmissions, status])
            current_time = send_time + 0.002


# ─────────────────────────────────────────────
#  YARDIMCI: ANALİZ ET
# ─────────────────────────────────────────────
def analyze(csv_file, packet_size_bytes=1024, payload_size_bytes=1000):
    """
    analyzer.py'nin sözlük döndüren versiyonu.
    Grafik çizmek için sayısal değerlere ihtiyacımız var.
    """
    df = pd.read_csv(csv_file)
    successful_df = df[df["status"] == "Success"]

    if successful_df.empty:
        return None  # Hiç başarılı paket yoksa atla

    start_time = df["send_time"].min()
    end_time   = successful_df["ack_time"].max()
    total_time = end_time - start_time

    if total_time <= 0:
        return None

    total_unique       = len(df)
    total_retrans      = df["retransmission_count"].sum()
    total_sent         = total_unique + total_retrans
    failed_count       = len(df[df["status"] == "Failed"])

    total_bytes  = total_sent * packet_size_bytes
    useful_bytes = len(successful_df) * payload_size_bytes

    throughput_mbps = (total_bytes  * 8) / total_time / 1_000_000
    goodput_mbps    = (useful_bytes * 8) / total_time / 1_000_000
    loss_rate_pct   = (total_retrans / total_sent) * 100 if total_sent > 0 else 0

    direct_df = df[df["is_timeout"] == 0]
    avg_rtt_ms = ((direct_df["ack_time"] - direct_df["send_time"]).mean() * 1000
                  if not direct_df.empty else 0)

    return {
        "throughput_mbps": round(throughput_mbps, 4),
        "goodput_mbps":    round(goodput_mbps,    4),
        "loss_rate_pct":   round(loss_rate_pct,   2),
        "avg_rtt_ms":      round(avg_rtt_ms,      2),
        "failed_count":    failed_count,
    }


# ─────────────────────────────────────────────
#  YARDIMCI: 4'LÜ GRAFİK ŞABLONU
# ─────────────────────────────────────────────
def plot_4metrics(x_values, results, x_label, title, filename):
    """
    Her senaryo için 4 metriği (Throughput, Goodput, Kayıp, RTT)
    aynı figürde 2x2 düzeninde çizer ve PNG olarak kaydeder.
    """
    throughputs = [r["throughput_mbps"] for r in results]
    goodputs    = [r["goodput_mbps"]    for r in results]
    loss_rates  = [r["loss_rate_pct"]   for r in results]
    avg_rtts    = [r["avg_rtt_ms"]      for r in results]

    fig = plt.figure(figsize=(12, 8))
    fig.suptitle(title, fontsize=14, fontweight="bold",
                 color="#cba6f7", y=0.98)

    gs = gridspec.GridSpec(2, 2, figure=fig,
                           hspace=0.45, wspace=0.35)

    subplots = [
        (gs[0, 0], throughputs, "Throughput (Mbps)",       COLORS[0], "Mbps"),
        (gs[0, 1], goodputs,    "Goodput (Mbps)",          COLORS[1], "Mbps"),
        (gs[1, 0], loss_rates,  "Paket Kayıp Oranı (%)",  COLORS[3], "%"),
        (gs[1, 1], avg_rtts,    "Ortalama RTT (ms)",       COLORS[2], "ms"),
    ]

    for spec, data, ylabel, color, unit in subplots:
        ax = fig.add_subplot(spec)
        bars = ax.bar([str(x) for x in x_values], data, color=color,
                      alpha=0.85, edgecolor="#ffffff22", linewidth=0.8)

        # Her barın üstüne değer yaz
        for bar, val in zip(bars, data):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + max(data) * 0.02,
                    f"{val:.2f}{unit}", ha="center", va="bottom",
                    fontsize=8, color="#ffffff99")

        ax.set_title(ylabel)
        ax.set_xlabel(x_label)
        ax.set_ylabel(ylabel)
        ax.grid(axis="y")
        ax.set_ylim(0, max(data) * 1.18 if max(data) > 0 else 1)

    out_path = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(out_path, dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  ✅  Kaydedildi → {out_path}")


# ─────────────────────────────────────────────
#  SENARYO 1: PAKET BOYUTUNUN ETKİSİ
# ─────────────────────────────────────────────
def senaryo1_paket_boyutu():
    """
    Sabit kayıp oranı (%15) ve timeout (0.5s) altında
    farklı paket boyutlarının (512B – 8192B) performansa etkisi.
    """
    print("\n[SENARYO 1] Paket Boyutunun Etkisi çalışıyor...")

    # Test edilecek paket boyutları (Byte)
    packet_sizes = [512, 1024, 2048, 4096, 8192]
    results = []

    for psize in packet_sizes:
        generate_log(TEMP_LOG, total_packets=500,
                     loss_rate=0.15, timeout_sec=0.5)
        payload = int(psize * 0.975)  # ~%2.5 header overhead varsayımı
        r = analyze(TEMP_LOG,
                    packet_size_bytes=psize,
                    payload_size_bytes=payload)
        if r:
            results.append(r)
            print(f"    {psize}B → Throughput: {r['throughput_mbps']} Mbps "
                  f"| Goodput: {r['goodput_mbps']} Mbps "
                  f"| RTT: {r['avg_rtt_ms']} ms")

    plot_4metrics(
        x_values=packet_sizes,
        results=results,
        x_label="Paket Boyutu (Byte)",
        title="Senaryo 1 – Paket Boyutunun Ağ Performansına Etkisi",
        filename="senaryo1_paket_boyutu.png",
    )


# ─────────────────────────────────────────────
#  SENARYO 2: TIMEOUT DEĞERİNİN ETKİSİ
# ─────────────────────────────────────────────
def senaryo2_timeout():
    """
    Sabit kayıp oranı (%15) ve paket boyutu (1024B) altında
    farklı timeout sürelerinin (0.1s – 2.0s) performansa etkisi.

    Beklenti: Timeout arttıkça throughput DÜŞMELİ çünkü
    kayıp olan paketin yeniden gönderilmesi için bekleme süresi uzuyor.
    """
    print("\n[SENARYO 2] Timeout Değerinin Etkisi çalışıyor...")

    timeout_values = [0.1, 0.25, 0.5, 1.0, 2.0]
    results = []

    for tval in timeout_values:
        generate_log(TEMP_LOG, total_packets=500,
                     loss_rate=0.15, timeout_sec=tval)
        r = analyze(TEMP_LOG,
                    packet_size_bytes=1024,
                    payload_size_bytes=1000)
        if r:
            results.append(r)
            print(f"    timeout={tval}s → Throughput: {r['throughput_mbps']} Mbps "
                  f"| RTT: {r['avg_rtt_ms']} ms")

    plot_4metrics(
        x_values=timeout_values,
        results=results,
        x_label="Timeout Süresi (saniye)",
        title="Senaryo 2 – Timeout Değerinin Ağ Performansına Etkisi",
        filename="senaryo2_timeout.png",
    )


# ─────────────────────────────────────────────
#  SENARYO 3: KAYIP ORANININ ETKİSİ
# ─────────────────────────────────────────────
def senaryo3_kayip_orani():
    """
    Sabit paket boyutu (1024B) ve timeout (0.5s) altında
    farklı kayıp oranlarının (%0 – %40) performansa etkisi.

    Beklenti: Kayıp oranı arttıkça hem throughput hem goodput DÜŞMELI,
    paket kayıp oranı metriği ise YÜKSELMELI.
    """
    print("\n[SENARYO 3] Kayıp Oranının Etkisi çalışıyor...")

    loss_rates = [0.00, 0.05, 0.10, 0.20, 0.30, 0.40]
    results = []

    for lr in loss_rates:
        generate_log(TEMP_LOG, total_packets=500,
                     loss_rate=lr, timeout_sec=0.5)
        r = analyze(TEMP_LOG,
                    packet_size_bytes=1024,
                    payload_size_bytes=1000)
        if r:
            results.append(r)
            print(f"    loss={int(lr*100)}% → Throughput: {r['throughput_mbps']} Mbps "
                  f"| Kayıp: %{r['loss_rate_pct']}")

    plot_4metrics(
        x_values=[f"%{int(lr*100)}" for lr in loss_rates],
        results=results,
        x_label="Simüle Edilmiş Kayıp Oranı",
        title="Senaryo 3 – Kayıp Oranının Ağ Performansına Etkisi",
        filename="senaryo3_kayip_orani.png",
    )


# ─────────────────────────────────────────────
#  SENARYO 4: DOSYA BOYUTUNUN ETKİSİ
# ─────────────────────────────────────────────
def senaryo4_dosya_boyutu():
    """
    Sabit kayıp oranı (%15), paket boyutu (1024B) ve timeout (0.5s) altında
    farklı dosya boyutlarının (100 – 5000 paket) performansa etkisi.

    Beklenti: Dosya büyüdükçe throughput STABILLEŞMELI çünkü
    başlangıç overhead'ı toplam süreye oranla küçülür (amortizasyon).
    """
    print("\n[SENARYO 4] Dosya Boyutunun Etkisi çalışıyor...")

    file_sizes_packets = [100, 250, 500, 1000, 2000, 5000]
    results = []

    for n in file_sizes_packets:
        generate_log(TEMP_LOG, total_packets=n,
                     loss_rate=0.15, timeout_sec=0.5)
        r = analyze(TEMP_LOG,
                    packet_size_bytes=1024,
                    payload_size_bytes=1000)
        if r:
            results.append(r)
            # Yaklaşık dosya boyutunu MB cinsinden hesapla
            approx_mb = round(n * 1000 / 1_000_000, 2)
            print(f"    {n} paket (~{approx_mb} MB) → "
                  f"Throughput: {r['throughput_mbps']} Mbps")

    plot_4metrics(
        x_values=[f"{n}pkt" for n in file_sizes_packets],
        results=results,
        x_label="Dosya Boyutu (Paket Sayısı)",
        title="Senaryo 4 – Dosya Boyutunun Ağ Performansına Etkisi",
        filename="senaryo4_dosya_boyutu.png",
    )


# ─────────────────────────────────────────────
#  ANA ÇALIŞTIRIC
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("  NetProbe – Deney Otomasyonu & Görselleştirme")
    print("=" * 55)

    senaryo1_paket_boyutu()
    senaryo2_timeout()
    senaryo3_kayip_orani()
    senaryo4_dosya_boyutu()

    # Geçici log dosyasını temizle
    if os.path.exists(TEMP_LOG):
        os.remove(TEMP_LOG)

    print("\n" + "=" * 55)
    print(f"  Tüm grafikler '{OUTPUT_DIR}/' klasörüne kaydedildi.")
    print("  Raporunuza ekleyebilirsiniz! 🎉")
    print("=" * 55)
