"""Generate the Billig (1967) shock-shape comparison figure for the VnV doc page.

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

from flow_theory.shock_shape import shock_shape_points

# --------------------------------------------------
# set directories/paths
# --------------------------------------------------
script_dir = Path(__file__).resolve().parent
case_dir = script_dir.parent

# --------------------------------------------------
# Storer's worked example quoted directly in Billig (1967): M=19.25 at
# 200,000 ft, sphere nose, gamma=1.4 (perfect gas)
# --------------------------------------------------
M_inf = 19.25
gamma = 1.4
R_nose = 1.0

x, y = shock_shape_points(M_inf, gamma, R_nose, n_pts=200)

# Billig's plot origin is at the sphere center (x_ours = +R_nose), not the
# nose tip (x_ours = 0) -- shift for the comparison
x_billig_frame = x - R_nose

fig, ax = plt.subplots(figsize=(6, 5.5))
ax.plot(x_billig_frame, y, label="flow_theory shock_shape_points()", color="black")
ax.plot(0.0, 1.6318612, "o", color="red", label="Billig (1967): y/R=1.64 at x/R=0")
ax.axvline(0.0, color="gray", linewidth=0.5, linestyle="--")
# Note: at M=19.25 the Mach angle is only ~3 deg, so the shock's freestream
# Mach-cone asymptote only becomes visually apparent hundreds of nose radii
# downstream -- far outside this near-nose plot range -- so it is omitted here.
ax.set_xlabel("x/R (Billig frame, origin at sphere center)")
ax.set_ylabel("y/R")
ax.set_title(f"Billig (1967) sphere shock shape, M={M_inf}, gamma={gamma}")
ax.legend(fontsize=8)
ax.set_xlim(-1, 3)
ax.set_ylim(0, 2)
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig(case_dir / "billig_shock_shape.png", dpi=150)
print("saved figure")
