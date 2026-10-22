#!/usr/bin/env python3
"""Reproduce manuscript Fig. 6: four base curves, EPS6 restart, and cIP6.

Data are read from the archived benchmark records. The cIP30 curve retains
the historical implementation; cIP6 uses the current implementation.
Use --data-dir to specify the kylin-pbc-v1.0-data archive root.
"""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
default_data = next((p for p in HERE.parents if (p / "scaling").is_dir()
                     and (p / "revision").is_dir()),
                    HERE.parents[2] / "kylin-pbc-v1.0-data")
parser.add_argument("--data-dir", type=Path, default=default_data)
parser.add_argument("--output", type=Path, default=HERE / "fig_scaling_time.png")
args = parser.parse_args()
ARCHIVE = args.data_dir.resolve()
RUN_ARCHIVE = ARCHIVE / "revision/kylin-cip6-scaling"
OUT = args.output.parent
OUT.mkdir(parents=True, exist_ok=True)
STEM = args.output.stem
os.environ.setdefault("MPLCONFIGDIR", "/tmp/kylin_sixcurves_mpl")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp/kylin_sixcurves_cache")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, NullLocator, ScalarFormatter
import numpy as np

SIZES = [16, 32, 64, 128, 256]
# Historical curves retain the manuscript's original millisecond rounding.
KYLIN_PBE = [3.394, 8.065, 13.889, 29.882, 72.094]
CP2K_PBE = [0.657, 1.113, 2.379, 4.618, 9.833]
KYLIN_HSE = [9.253, 26.148, 89.170, 470.462, 2191.967]
CP2K_4C_A = [75.378, 168.096, 629.707, 2228.596, 8628.353]
PAPER_SCRIPT = Path(__file__).resolve()


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def timer(path, code):
    text = Path(path).read_text()
    if code == "kylin":
        assert "SCF converged in" in text and "Kylin-PBC Done." in text
        return float(re.findall(r'Timer "Kylin-PBC main" used time:\s*([\d.]+)', text)[-1])
    assert "SCF run converged" in text and "PROGRAM ENDED" in text
    return float(re.findall(r"^\s*CP2K\s+1\s+.*$", text, re.M)[-1].split()[-1])


def main():
    base = {"KYLIN_PBE": KYLIN_PBE, "CP2K_PBE": CP2K_PBE,
            "KYLIN_HSE": KYLIN_HSE, "CP2K_4C_A": CP2K_4C_A}
    manifest = json.loads((RUN_ARCHIVE / "source-records/manifest.json").read_text())
    summary = json.loads((RUN_ARCHIVE / "source-records/summary.json").read_text())
    selected = json.loads((RUN_ARCHIVE / "source-records/selected.json").read_text())
    assert selected["c_ip"] == 6 and summary["production_complete"]
    production = sorted(
        (row for row in summary["results"] if row["kind"] == "production"),
        key=lambda row: row["atoms"])
    assert [row["atoms"] for row in production] == SIZES
    assert all(row["complete"] and row["c_ip"] == 6 for row in production)
    restart = sorted(manifest["cp2k_baseline"], key=lambda row: row["atoms"])
    assert [row["atoms"] for row in restart] == SIZES
    data = {
        "kylin_pbe_original": base["KYLIN_PBE"],
        "cp2k_pbe_original": base["CP2K_PBE"],
        "kylin_hse_original": base["KYLIN_HSE"],
        "cp2k_hse_atomic_4c": base["CP2K_4C_A"],
        "cp2k_hse_restart_eps6": [row["total_seconds"] for row in restart],
        "kylin_hse_cip6": [row["total_seconds"] for row in production],
    }
    provenance = {"manuscript_plot_script": str(PAPER_SCRIPT),
                  "manuscript_plot_script_sha256": sha256(PAPER_SCRIPT),
                  "sources": {}, "series": data}
    for i, n in enumerate(SIZES):
        sources = {
            "kylin_pbe_original": ARCHIVE / f"scaling/Si{n}-PBE/kylin-pbc.log",
            "cp2k_pbe_original": ARCHIVE / f"scaling/Si{n}-PBE/cp2k.log",
            "kylin_hse_original": ARCHIVE / f"scaling/Si{n}-HSE06/kylin-pbc.log",
            "cp2k_hse_atomic_4c": ARCHIVE / f"revision/cp2k-4c-hfx/atomic-guess/Si{n}-HSE06/cp2k.log",
            "kylin_hse_cip6": RUN_ARCHIVE / f"cases/Si{n}_selected_c06/run.log",
        }
        for key, path in sources.items():
            actual = timer(path, "kylin" if key.startswith("kylin") else "cp2k")
            assert abs(actual - data[key][i]) <= 0.00051, (key, n, actual)
        for stage, filename in [("hse", "cp2k.log"), ("pbe", "pbe.log")]:
            original = next(p for p in restart[i]["source_paths"]
                            if p.endswith("/" + filename))
            archived = ARCHIVE / f"revision/cp2k-4c-hfx/pbe-restart/Si{n}-HSE06/{filename}"
            # The same historical Si16 PBE stage is archived with EPS8.
            if n == 16 and stage == "pbe":
                archived = ARCHIVE / "revision/cp2k-4c-hfx/pbe-restart-eps8/Si16-HSE06/pbe.log"
            assert sha256(archived) == restart[i]["source_sha256"][original]
            sources[f"cp2k_hse_restart_eps6_{stage}"] = archived
        actual_restart = sum(timer(sources[k], "cp2k") for k in [
            "cp2k_hse_restart_eps6_hse", "cp2k_hse_restart_eps6_pbe"])
        assert abs(actual_restart - data["cp2k_hse_restart_eps6"][i]) < 1e-6
        provenance["sources"][str(n)] = {
            key: {"path": str(path), "sha256": sha256(path)}
            for key, path in sources.items()}
    provenance["notes"] = [
        "Four base curves are taken from the CURRENT revised manuscript, not the original-submission RI-HFX/ADMM curve.",
        "CP2K restart is original cpFIT3 at EPS_SCHWARZ=1e-6, including its historical PBE stage.",
        "All cIP6 production points use the current frozen executable, 32 threads, cpu32/cu03, ON/EWALD.",
        "Historical Kylin timings use a different implementation; historical Si256 uses OFF/NONE.",
        "cIP6 is calibrated on Si64; Si256 accuracy has no FFTDF-reference validation.",
    ]
    provenance["loglog_slopes"] = {
        key: float(np.polyfit(np.log(SIZES), np.log(values), 1)[0])
        for key, values in data.items()}
    (OUT / f"{STEM}_provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
    with (OUT / f"{STEM}_timings.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["atoms"] + list(data))
        for i, n in enumerate(SIZES):
            writer.writerow([n] + [values[i] for values in data.values()])

    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 11,
        "axes.labelsize": 12, "legend.fontsize": 9.8,
        "axes.spines.top": False, "axes.spines.right": False,
        "pdf.fonttype": 42, "ps.fonttype": 42,
    })
    fig, ax = plt.subplots(figsize=(7.5, 6.0))
    fig.subplots_adjust(left=0.115, right=0.975, top=0.972, bottom=0.274)
    styles = [
        ("kylin_pbe_original", "Kylin-PBC PBE", "#2196F3", "o", "-"),
        ("cp2k_pbe_original", "CP2K PBE", "#1565C0", "o", "--"),
        ("kylin_hse_original", r"Kylin-PBC HSE06 ($c_{\rm IP}=30$)", "#E64B35", "s", "-"),
        ("cp2k_hse_atomic_4c", "CP2K HSE06 (4-center, atomic)", "#9C27B0", "^", "--"),
        ("cp2k_hse_restart_eps6", "CP2K HSE06 (PBE restart)", "#6A1B9A", "v", ":"),
        ("kylin_hse_cip6", r"Kylin-PBC HSE06 ($c_{\rm IP}=6$)", "#16855D", "D", "-"),
    ]
    handles = {}
    for key, label, color, marker, ls in styles:
        line, = ax.plot(SIZES, data[key], color=color, marker=marker,
                        ls=ls, lw=2.1 if key == "kylin_hse_cip6" else 1.8,
                        ms=6, label=label, zorder=4 if key == "kylin_hse_cip6" else 3)
        handles[key] = line
    ax.set_xscale("log", base=2)
    ax.set_yscale("log")
    ax.set_xlim(13.5, 300)
    ax.set_ylim(0.45, 15000)
    ax.xaxis.set_major_locator(FixedLocator(SIZES))
    ax.xaxis.set_major_formatter(ScalarFormatter())
    ax.xaxis.set_minor_locator(NullLocator())
    ax.yaxis.set_minor_locator(NullLocator())
    ax.set_xlabel("Number of Si atoms")
    ax.set_ylabel("SCF wall time (s)")
    ax.grid(axis="y", which="major", color="#D9DDE2", lw=0.7)
    order = ["kylin_pbe_original", "kylin_hse_original", "kylin_hse_cip6",
             "cp2k_pbe_original", "cp2k_hse_atomic_4c", "cp2k_hse_restart_eps6"]
    ax.legend(handles=[handles[k] for k in order], ncol=2, frameon=False,
              loc="upper center", bbox_to_anchor=(0.5, -0.175),
              handlelength=2.2, columnspacing=1.7, labelspacing=0.9)
    for extension in ["png", "pdf", "svg"]:
        fig.savefig(OUT / f"{STEM}.{extension}", dpi=300)
    plt.close(fig)
    print(OUT / f"{STEM}.png")


if __name__ == "__main__":
    main()
