# van Driest II Method

The van Driest II method maps a compressible turbulent boundary layer to an
equivalent incompressible one, evaluates the incompressible turbulent skin
friction law, then maps back to compressible form[^van_driest_1951].

The turbulent mapping structure is documented in
[Turbulent Estimates](turbulent.md).


The van Driest II correction factors are

$$
F_c = \frac{rm}{\left[\sin^{-1}(\alpha) + \sin^{-1}(\beta)\right]^2},
$$

$$
F_x = \frac{\mu_e/\mu_w}{F_c}.
$$

where \(\mu_e = \mu(T_e)\) and \(\mu_w = \mu(T_w)\).

$\alpha$ and $\beta$ are defined as


$$
\alpha = \frac{2a^2 - b}{D},
\quad
\beta = \frac{b}{D}.
$$

$a$, $b$, and $D$ are

$$
a = \sqrt{\frac{mr}{F}},
\quad
b = \frac{1 + rm - F}{F},
\quad
D = \sqrt{4a^2 + b^2},
$$

with $m$, $r$, and $F$ as

$$
m = \frac{\gamma-1}{2}M_e^2,
\quad
r = \mathrm{Pr}^{1/3},
\quad
F = \frac{T_w}{T_e}.
$$






## References

[^van_driest_1951]: Van Driest, E.R. (1951). *Turbulent boundary layer in compressible fluids*. Journal of the Aeronautical Sciences, 18(3), 145-160.
