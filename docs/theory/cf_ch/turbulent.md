# Turbulent Estimates

The turbulent skin-friction estimates map the incompressible
Karman-Schoenherr relation[^schoenherr_1932] to the compressible case using the
correction factors \(F_x\) and \(F_c\). The factor \(F_x\) maps the Reynolds
number to an equivalent incompressible Reynolds number.

The incompressible turbulent average skin-friction relation by Karman-Schoenherr [^schoenherr_1932] is:

$$
\frac{0.242}{\sqrt{C_{f,\mathrm{inc}}}}
=
\log_{10}\!\left(\mathrm{Re}_{x,\mathrm{inc}}\,C_{f,\mathrm{inc}}\right).
$$

The average coefficient is converted to the local incompressible coefficient
with the Hopkins-Inouye relation[^hopkins_inouye_1971]:

$$
c_{f,\mathrm{inc}}
=
\frac{0.242\,C_{f,\mathrm{inc}}}
{0.242 + 0.8686\sqrt{C_{f,\mathrm{inc}}}}.
$$

The mapping is done with the correction factors \(F_x\) and \(F_c\):

$$
\mathrm{Re}_{x,\mathrm{inc}} = F_x\,\mathrm{Re}_x
$$

$$
c_f = \frac{c_{f,\mathrm{inc}}}{F_c}.
$$

For all turbulent methods, the Stanton number is then computed from Reynolds analogy:

$$
C_h = \frac{c_f}{2\,\mathrm{Pr}^{2/3}}.
$$

The only method-specific part is how \(F_x\) and \(F_c\) are computed:

- [van Driest II](van_driest_ii.md)
- [Spalding-Chi (1964)](spalding_chi_1964.md)
- [Sommer-Short](sommer_short.md)
- [White-Christoph](white_christoph.md)

## References

[^schoenherr_1932]: Schoenherr, K.E. (1932). *Resistance of flat surfaces moving through a fluid*. Trans. SNAME, 40, 279-313.
[^hopkins_inouye_1971]: Hopkins, E.J. and Inouye, M. (1971). *An evaluation of theories for predicting turbulent skin friction and heat transfer on flat plates at supersonic and hypersonic Mach numbers*. NASA TN D-6353.
