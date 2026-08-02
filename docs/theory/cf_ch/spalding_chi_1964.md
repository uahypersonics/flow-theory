# Spalding-Chi (1964) Method

This turbulent method keeps the same incompressible Karman-Schoenherr backbone as
the other turbulent methods and uses the compressibility transformation summarized
by Hopkins and Inouye[^hopkins_inouye_1971].

The shared turbulent mapping structure is documented in
[Turbulent Estimates](turbulent.md).

The Spalding-Chi correction factors are

$$
F_c = \frac{rm}{\left[\sin^{-1}(\alpha) + \sin^{-1}(\beta)\right]^2},
$$

$$
F_x = \frac{F_\theta}{F_c},
$$

where

$$
F_\theta = \frac{1}{F^{0.702}F_{aw}^{0.772}}.
$$

The temperature ratios are

$$
F = \frac{T_w}{T_e},
\qquad
F_{aw} = \frac{T_w}{T_{aw}},
\qquad
\frac{T_{aw}}{T_e} = 1 + rm.
$$

The remaining factors match the van Driest II transformation:

$$
m = \frac{\gamma-1}{2}M_e^2,
\qquad
r = \mathrm{Pr}^{1/3},
$$

$$
a = \sqrt{\frac{mr}{F}},
\qquad
b = \frac{1 + rm - F}{F},
\qquad
D = \sqrt{4a^2+b^2},
$$

$$
\alpha = \frac{2a^2-b}{D},
\qquad
\beta = \frac{b}{D}.
$$

## References

[^hopkins_inouye_1971]: Hopkins, E.J. and Inouye, M. (1971). *An evaluation of theories for predicting turbulent skin friction and heat transfer on flat plates at supersonic and hypersonic Mach numbers*. NASA TN D-6353.
