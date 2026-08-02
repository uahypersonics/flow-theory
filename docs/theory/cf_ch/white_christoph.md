# White-Christoph Method

The White-Christoph method is a simplified closed-form approximation to
van Driest II-style turbulent compressibility transformation[^white_christoph_1972].

The shared turbulent mapping structure is documented in
[Turbulent Estimates](turbulent.md).

The White-Christoph correction factors are

$$
F_c = S^2,
$$

$$
F_x = \frac{\mu_e}{\mu_w}\,\frac{1}{\sqrt{F}\,S},
$$

where \(\mu_e = \mu(T_e)\) and \(\mu_w = \mu(T_w)\).

The required factors are defined as

$$
m = \frac{\gamma-1}{2}M_e^2,
\qquad
r = \mathrm{Pr}^{1/3},
$$

and

$$
F = \frac{T_w}{T_e},
\qquad
\frac{T_{aw}}{T_e} = 1 + rm,
\qquad
F_{aw} = \frac{T_w}{T_{aw}} = \frac{F}{T_{aw}/T_e}.
$$

With those the following values can be computed

$$
a = \sqrt{\frac{m}{F}},
\qquad
b = \frac{1 - F_{aw}}{F_{aw}},
\qquad
D = \sqrt{4a^2 + b^2},
$$

$$
\alpha = \frac{2a^2 - b}{D},
\qquad
\beta = \frac{b}{D},
$$

$$
S = \frac{\sqrt{F/F_{aw} - 1}}{\sin^{-1}(\alpha) + \sin^{-1}(\beta)}.
$$

## References

[^white_christoph_1972]: White, F.M. and Christoph, G.H. (1972). *A simple new analysis of the turbulent compressible boundary layer*. AIAA Paper 70-164.
