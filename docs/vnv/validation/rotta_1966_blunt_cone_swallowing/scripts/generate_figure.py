"""Generate the Rotta (1966) Fig. 9 comparison figure for the VnV doc page.

matplotlib is intentionally not a project dependency (`pip install matplotlib`
before running), matching the precedent in similarity-bl's own VnV scripts.
"""

# --------------------------------------------------
# import necessary modules
# --------------------------------------------------
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from flow_theory.entropy_swallowing import swallowing_distance

# --------------------------------------------------
# set directories/paths
# --------------------------------------------------
script_dir = Path(__file__).resolve().parent
case_dir = script_dir.parent

# --------------------------------------------------
# digitized data from Rotta (1966), Fig. 9 (page 26 / PDF p.35), solid
# "numerical integration of Eq. (16)" curves -- read off the plot by eye,
# approximate to within about +/-10% of plot resolution
# --------------------------------------------------
rotta_fig9 = {
    5: {"M": [4, 6, 8, 10, 12, 14, 16, 18], "Sc_Re13": [2.0, 9.0, 13.0, 14.3, 14.6, 14.5, 14.2, 14.0]},
    10: {"M": [4, 6, 8, 10, 12, 14, 16, 18], "Sc_Re13": [1.0, 3.7, 4.0, 4.0, 3.9, 3.8, 3.6, 3.4]},
    15: {"M": [4, 6, 8, 10, 12, 14, 16, 18], "Sc_Re13": [0.5, 1.9, 2.0, 2.0, 1.9, 1.85, 1.8, 1.75]},
    20: {"M": [4, 6, 8, 10, 12, 14, 16, 18], "Sc_Re13": [0.3, 1.0, 1.0, 0.95, 0.9, 0.85, 0.8, 0.75]},
}

# --------------------------------------------------
# flow_theory computed swallowing distance, non-dimensionalized by nose
# radius, over the same Mach range Rotta studied
# --------------------------------------------------
R_nose = 0.0254  # 1 inch, representative blunted-cone nose radius
Re1 = 3.0e6  # 1/m, representative unit Reynolds number
Tw_T0 = 0.4  # representative cold-wall ratio

mach_ft = np.linspace(5.0, 18.0, 27)
x_sw_over_R = []
for M in mach_ft:
    x_sw = swallowing_distance(R_nose, Re1, float(M), Tw_T0)
    x_sw_over_R.append(x_sw / R_nose)

# --------------------------------------------------
# build the two-panel comparison figure
# --------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))

for angle, data in rotta_fig9.items():
    ax1.plot(data["M"], data["Sc_Re13"], marker="o", label=f"{angle} deg")
ax1.set_xlabel("Freestream Mach number, M_inf")
ax1.set_ylabel(r"$\bar{S}_c / Re_{\theta 0}^{1/3}$")
ax1.set_title("Rotta (1966) Fig. 9\n(digitized, numerical-integration curves)")
ax1.legend(title="Cone half-angle")
ax1.grid(True, alpha=0.3)

ax2.plot(mach_ft, x_sw_over_R, color="black")
ax2.set_xlabel("Edge Mach number, Me")
ax2.set_ylabel(r"$x_\mathrm{sw} / R_\mathrm{nose}$")
ax2.set_yscale("log")
ax2.set_title(
    "flow_theory swallowing_distance()\n(R_nose=1 in, Re1=3e6 1/m, Tw/T0=0.4)"
)
ax2.grid(True, alpha=0.3)

fig.tight_layout()
fig.savefig(case_dir / "rotta_fig9_vs_flow_theory.png", dpi=150)
print("saved figure")
