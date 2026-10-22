#!/usr/bin/env python3
"""Revised Fig. 6 (fig_scaling_time.png) for the revised manuscript.

Same data and style as art/example/scaling/18_paper_figs.py for the Kylin-PBC
(PBE/MGDF, HSE06/LISDF) and CP2K PBE (GPW) curves; the CP2K HSE06 curve of the
original submission (RI-HFX/ADMM) is replaced by the four-center HFX/ADMM
timings of the revision. The atomic-guess series uses EPS_SCHWARZ=1e-6;
the PBE-restart series uses 1e-8 with density screening at every size and
includes the historical PBE step. The restart data are read from the archived
summary. All restart runs used cpu32/512 GB nodes; Si256 recomputed about
28% of its ERIs per iteration. Open symbols mark runs on the 2 TB node
(Kylin-PBC Si256; CP2K atomic-guess Si256).
"""
import argparse
import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/kylin_eps8_mpl")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp/kylin_eps8_cache")
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
default_data = (Path(HERE).parents[2] / "kylin-pbc-v1.0-data" / "revision" /
                "cp2k-4c-hfx" / "pbe-restart-eps8")
# The archived copy of this script lives next to summary_eps8.json.
if (Path(HERE) / "summary_eps8.json").exists():
    default_data = Path(HERE)
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--data-dir", type=Path, default=default_data)
parser.add_argument("--output", type=Path, default=Path(HERE) / "fig_scaling_time.png")
args = parser.parse_args()
SIZES = [16, 32, 64, 128, 256]

# Kylin-PBC and CP2K PBE totals: unchanged from the original submission
# (parsed from art/example/scaling/Si{N}-{PBE,HSE06}/{kylin-pbc,cp2k}.log).
KYLIN_PBE = [3.394, 8.065, 13.889, 29.882, 72.094]
CP2K_PBE = [0.657, 1.113, 2.379, 4.618, 9.833]
KYLIN_HSE = [9.253, 26.148, 89.170, 470.462, 2191.967]
# CP2K four-center HFX/ADMM (libint, EPS_SCHWARZ 1e-6, in-core, ADMMS/cpFIT3), 32 ranks
# (a) atomic guess, no density-matrix screening; Si256 on the 2 TB node
CP2K_4C_A = [75.378, 168.096, 629.707, 2228.596, 8628.353]
# (b) EPS_SCHWARZ=1e-8, PBE restart + SCREEN_ON_INITIAL_P at all sizes.
summary = json.loads((args.data_dir / "summary_eps8.json").read_text())
restart_rows = sorted(summary["results"], key=lambda row: row["atoms"])
assert [row["atoms"] for row in restart_rows] == SIZES
CP2K_4C_B = [row["cp2k_total_including_pbe_seconds"] for row in restart_rows]

plt.rcParams.update({"font.size": 9, "axes.titlesize": 9, "legend.fontsize": 8,
                     "xtick.labelsize": 8, "ytick.labelsize": 8})


def slope(ns, ys):
    ns, ys = np.array(ns, float), np.array(ys, float)
    return np.polyfit(np.log(ns), np.log(ys), 1)[0]


fig, ax = plt.subplots(figsize=(3.5, 3.9))


def pl(ns, ys, label, color, marker, ls="-", open_last=False):
    a = slope(ns, ys)
    if open_last:
        ax.loglog(ns[:-1], ys[:-1], marker=marker, lw=1.6, ms=5, color=color, ls=ls,
                  label=f"{label} ($N^{{{a:.2f}}}$)")
        ax.loglog(ns[-2:], ys[-2:], lw=1.6, color=color, ls=ls)
        ax.loglog(ns[-1:], ys[-1:], marker=marker, ms=5.5, color=color, ls="none",
                  markerfacecolor="white", markeredgewidth=1.4)
    else:
        ax.loglog(ns, ys, marker=marker, lw=1.6, ms=5, color=color, ls=ls,
                  label=f"{label} ($N^{{{a:.2f}}}$)")


pl(SIZES, KYLIN_PBE, "PBE   Kylin-PBC", "#2196F3", "o")
pl(SIZES, CP2K_PBE, "PBE   CP2K", "#1565C0", "o", "--")
pl(SIZES, KYLIN_HSE, "HSE06 Kylin-PBC", "#F44336", "s", open_last=True)
pl(SIZES, CP2K_4C_A, "HSE06 CP2K, atomic guess", "#9C27B0", "^", "--", open_last=True)
pl(SIZES, CP2K_4C_B, "HSE06 CP2K, PBE restart", "#6A1B9A", "v", ":")

ax.set_xlabel("Number of Si atoms")
ax.set_ylabel("SCF wall time (s)")
ax.set_xticks(SIZES)
ax.set_xticklabels([str(n) for n in SIZES])
ax.xaxis.set_minor_formatter(plt.NullFormatter())
ax.xaxis.set_minor_locator(plt.NullLocator())
ax.yaxis.set_minor_locator(plt.NullLocator())
ax.grid(True, which="major", ls=":", alpha=.5)
ax.legend(ncol=1, handlelength=2.0, loc="upper center", bbox_to_anchor=(0.5, -0.17),
          frameon=False, prop={"size": 7})
fig.tight_layout(pad=0.3)
out = args.output
fig.savefig(out, dpi=300, bbox_inches="tight")
print("saved", out)
