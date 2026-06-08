import os
import sys
import time
import subprocess
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

OUTPUT_DIR = "graphs"
TEMP_LOG   = "temp_scenario.csv"
TEMP_FILE  = "temp_data.bin"

os.makedirs(OUTPUT_DIR, exist_ok=True)

plt.rcParams.update({
    "figure.facecolor": "#1e1e2e", "axes.facecolor": "#2a2a3e",
    "axes.edgecolor": "#555577", "axes.labelcolor": "#cdd6f4",
    "xtick.color": "#cdd6f4", "ytick.color": "#cdd6f4",
    "text.color": "#cdd6f4", "grid.color": "#3a3a5a",
    "grid.linestyle": "--", "grid.alpha": 0.5,
    "font.family": "monospace", "font.size": 10,
})
COLORS = ["#89b4fa", "#a6e3a1", "#fab387", "#f38ba8", "#cba6f7"]

def run_real_test(file_size_bytes, payload_size, timeout_sec, loss_rate):
    with open(TEMP_FILE, "wb") as f:
        f.write(os.urandom(file_size_bytes))

    server_proc = subprocess.Popen([sys.executable, "-m", "server.server", str(loss_rate)])
    time.sleep(1) 

    subprocess.run([
        sys.executable, "-m", "client.client",
        "--file", TEMP_FILE,
        "--payload", str(payload_size),
        "--timeout", str(timeout_sec),
        "--log", TEMP_LOG
    ], capture_output=True) 

    server_proc.terminate()
    server_proc.wait()

def analyze(csv_file, payload_size_bytes):
    if not os.path.exists(csv_file):
        return None
        
    df = pd.read_csv(csv_file)
    successful_df = df[df["status"] == "Success"]

    if successful_df.empty:
        return None

    start_time = df["send_time"].min()
    end_time   = successful_df["ack_time"].max()
    total_time = end_time - start_time

    if total_time <= 0: return None

    total_sent = len(df) + df["retransmission_count"].sum()
    total_bytes = total_sent * payload_size_bytes 
    useful_bytes = len(successful_df) * payload_size_bytes

    throughput_mbps = (total_bytes * 8) / total_time / 1_000_000
    goodput_mbps    = (useful_bytes * 8) / total_time / 1_000_000
    loss_rate_pct   = (df["retransmission_count"].sum() / total_sent) * 100 if total_sent > 0 else 0

    direct_df = df[df["is_timeout"] == 0]
    avg_rtt_ms = ((direct_df["ack_time"] - direct_df["send_time"]).mean() * 1000 if not direct_df.empty else 0)

    return {
        "throughput_mbps": round(throughput_mbps, 4),
        "goodput_mbps":    round(goodput_mbps,    4),
        "loss_rate_pct":   round(loss_rate_pct,   2),
        "avg_rtt_ms":      round(avg_rtt_ms,      2),
    }

def plot_4metrics(x_values, results, x_label, title, filename):
    throughputs = [r["throughput_mbps"] for r in results]
    goodputs    = [r["goodput_mbps"]    for r in results]
    loss_rates  = [r["loss_rate_pct"]   for r in results]
    avg_rtts    = [r["avg_rtt_ms"]      for r in results]

    fig = plt.figure(figsize=(12, 8))
    fig.suptitle(title, fontsize=14, fontweight="bold", color="#cba6f7", y=0.98)
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.45, wspace=0.35)

    subplots = [
        (gs[0, 0], throughputs, "Throughput (Mbps)",       COLORS[0], "Mbps"),
        (gs[0, 1], goodputs,    "Goodput (Mbps)",          COLORS[1], "Mbps"),
        (gs[1, 0], loss_rates,  "Paket Kayip Orani (%)",  COLORS[3], "%"),
        (gs[1, 1], avg_rtts,    "Ortalama RTT (ms)",       COLORS[2], "ms"),
    ]

    for spec, data, ylabel, color, unit in subplots:
        ax = fig.add_subplot(spec)
        bars = ax.bar([str(x) for x in x_values], data, color=color, alpha=0.85, edgecolor="#ffffff22")
        for bar, val in zip(bars, data):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                    f"{val:.2f}{unit}", ha="center", va="bottom", fontsize=8, color="#ffffff99")
        ax.set_title(ylabel)
        ax.set_xlabel(x_label)
        ax.set_ylabel(ylabel)

    out_path = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(out_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)

def senaryo1_paket_boyutu():
    print("\n[SENARYO 1] Paket Boyutunun Etkisi...")
    packet_sizes = [512, 1024, 2048, 4096, 8192]
    results = []
    
    for psize in packet_sizes:
        print(f" -> {psize} Byte paketi test ediliyor...")
        run_real_test(file_size_bytes=100_000, payload_size=psize, timeout_sec=0.5, loss_rate=0.15)
        r = analyze(TEMP_LOG, psize)
        if r: results.append(r)
            
    plot_4metrics(packet_sizes, results, "Paket Boyutu (Byte)", "Senaryo 1 - Paket Boyutu", "senaryo1_paket_boyutu.png")

def senaryo2_timeout():
    print("\n[SENARYO 2] Timeout Degerinin Etkisi...")
    timeout_values = [0.1, 0.25, 0.5, 1.0, 2.0]
    results = []
    
    for tval in timeout_values:
        print(f" -> {tval} saniye timeout test ediliyor...")
        run_real_test(file_size_bytes=100_000, payload_size=1024, timeout_sec=tval, loss_rate=0.15)
        r = analyze(TEMP_LOG, 1024)
        if r: results.append(r)
            
    plot_4metrics(timeout_values, results, "Timeout (s)", "Senaryo 2 - Timeout", "senaryo2_timeout.png")

def senaryo3_kayip_orani():
    print("\n[SENARYO 3] Kayip Oraninin Etkisi...")
    loss_rates = [0.00, 0.05, 0.10, 0.20, 0.30]
    results = []
    
    for lr in loss_rates:
        print(f" -> %{int(lr*100)} kayip orani test ediliyor...")
        run_real_test(file_size_bytes=100_000, payload_size=1024, timeout_sec=0.5, loss_rate=lr)
        r = analyze(TEMP_LOG, 1024)
        if r: results.append(r)
            
    plot_4metrics([f"%{int(lr*100)}" for lr in loss_rates], results, "Kayip Orani", "Senaryo 3 - Kayip Orani", "senaryo3_kayip_orani.png")

def senaryo4_dosya_boyutu():
    print("\n[SENARYO 4] Dosya Boyutunun Etkisi...")
    file_sizes_kb = [50, 100, 250, 500, 1000]
    results = []
    
    for kb in file_sizes_kb:
        print(f" -> {kb} KB dosya test ediliyor...")
        run_real_test(file_size_bytes=kb*1024, payload_size=1024, timeout_sec=0.5, loss_rate=0.15)
        r = analyze(TEMP_LOG, 1024)
        if r: results.append(r)
            
    plot_4metrics([f"{kb}KB" for kb in file_sizes_kb], results, "Dosya Boyutu", "Senaryo 4 - Dosya Boyutu", "senaryo4_dosya_boyutu.png")

if __name__ == "__main__":
    print("=" * 55)
    print("  NetProbe - DENEY OTOMASYONU")
    print("=" * 55)

    senaryo1_paket_boyutu()
    senaryo2_timeout()
    senaryo3_kayip_orani()
    senaryo4_dosya_boyutu()

    if os.path.exists(TEMP_LOG): os.remove(TEMP_LOG)
    if os.path.exists(TEMP_FILE): os.remove(TEMP_FILE)
    if os.path.exists("alinan_dosya.dat"): os.remove("alinan_dosya.dat")

    print("\nTüm testler tamamlandi. Grafikler kaydedildi.")
