# Bow-Shock Standoff Distance

`flow_theory.shock_standoff` provides the Billig (1967)[^billig_1967]
empirical correlation for the normal-shock standoff distance ahead of a
blunt hypersonic body.

## Sphere

The non-dimensional standoff distance on a sphere is fit as

$$\frac{\Delta}{R_\mathrm{nose}} = 0.143 \exp\!\left(\frac{3.24}{M_\infty^2}\right)$$

for air ($\gamma = 1.4$). To generalize to other $\gamma$, the coefficient is
rescaled by the ratio of the $M_\infty \to \infty$ normal-shock density
ratio $\epsilon = (\gamma-1)/(\gamma+1)$ for the given $\gamma$ to that of
air, so the sphere formula recovers Billig's published fit exactly at
$\gamma=1.4$ and preserves the correct physical trend (standoff scales with
shock density ratio) for other $\gamma$.

## Sphere-Cone

The stagnation-region standoff distance is governed mainly by the local
subsonic pocket behind the normal shock near the stagnation streamline,
which is only weakly sensitive to the downstream body shape. `flow_theory`
approximates the sphere-cone standoff as the sphere value scaled by
$\sin(\theta_c)$, where $\theta_c$ is the cone half-angle:

$$\Delta_\mathrm{cone} = \Delta_\mathrm{sphere} \sin(\theta_c)$$

This captures the two known limits: a very blunt "cone"
($\theta_c \to 90°$, i.e. a flat-faced/disk-like body) recovers the full
sphere standoff, while a slender cone ($\theta_c \to 0°$) shrinks the
standoff toward zero as the bow shock approaches attachment. This is an
engineering approximation, not a literal digitization of a sphere-cone
standoff table.

[^billig_1967]: Billig, F.S. (1967). *Shock-wave shapes around spherical- and cylindrical-nosed bodies*. J. Spacecraft Rockets, 4(6), 822-823.
