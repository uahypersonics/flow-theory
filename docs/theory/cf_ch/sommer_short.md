# Sommer-Short Method

The Sommer-Short method maps compressible turbulent skin friction to the
incompressible Karman-Schoenherr relation using an empirical reference
temperature derived from free-flight drag measurements.[^sommer_short_1955]

The reference-temperature ratio is

$$
\frac{T'_{SS}}{T_e}
=
1 + 0.035M_e^2 + 0.45\left(\frac{T_w}{T_e} - 1\right).
$$

The transformation factors are

$$
F_c = \frac{T'_{SS}}{T_e},
$$

$$
F_\theta = \frac{\mu_e}{\mu'_{SS}},
$$

and, because these factors are constant along the plate,

$$
F_x = \frac{F_\theta}{F_c}.
$$

Here $\mu'_{SS}=\mu(T'_{SS})$. The shared turbulent mapping from $F_x$ and
$F_c$ to local compressible skin friction is documented in
[Turbulent Estimates](turbulent.md).

## References

[^sommer_short_1955]: Sommer, S.C. and Short, B.J. (1955). *Free-flight measurements of turbulent boundary-layer skin friction in the presence of severe aerodynamic heating at Mach numbers from 2.8 to 7.0*. NACA TN 3391.