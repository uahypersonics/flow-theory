# Bow-Shock Shape

`flow_theory.shock_shape` extends the [standoff distance](shock_standoff.md)
to the full detached bow-shock locus using Billig's (1967)[^billig_1967]
hyperbola fit.

## Coordinate Convention

The body nose tip is at $x=0$, with the freestream flowing in the $+x$
direction. The detached bow shock stands off *upstream* of the nose
(negative $x$) by the standoff distance $\Delta$ at the axis ($s=0$), then
sweeps back downstream (increasing $x$) as the lateral distance $s$ from
the axis increases, approaching the freestream Mach cone asymptote far from
the nose (see the
[Billig (1967) validation case](../vnv/validation/billig_1967_shock_shape/index.md)).

## Hyperbola Fit

$$x_\mathrm{shock}(s) = -\Delta + R_c \cot^2\theta\left(\sqrt{1 + \tan^2\theta\, \frac{s^2}{R_c^2}} - 1\right)$$

where:

- $\Delta$ is the axis standoff distance from [`standoff_sphere`](shock_standoff.md)
- $R_c = 1.143 \exp\!\left(0.54/(M_\infty - 1)^{1.2}\right) R_\mathrm{nose}$ is the shock radius of curvature at the nose
- $\theta = \arcsin(1/M_\infty)$ is the asymptotic shock wave angle (the Mach angle, since far from the nose the shock approaches the freestream Mach cone for a body with no continuing cone half-angle)

[^billig_1967]: Billig, F.S. (1967). *Shock-wave shapes around spherical- and cylindrical-nosed bodies*. J. Spacecraft Rockets, 4(6), 822-823.
