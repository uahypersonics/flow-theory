# Eckert Reference-Temperature Method

This method is a compressible correction of the Blasius laminar estimate,
applied through a reference temperature \(T^*\).

It keeps the same [Blasius](blasius.md) skin-friction form and replaces
\(\mathrm{Re}_x\) with a corrected local Reynolds number \(\mathrm{Re}_x^*\).

The reference temperature based on [^1][^2] is

$$
\frac{T^*}{T_e} = 0.5 + 0.039 M_e^2 + 0.5\frac{T_w}{T_e}
$$

??? note "Alternative reference temperature equations"
	A common alternative form of the reference temperature written with recovery temperature is

	$$
	T^* = T_e + 0.5\,(T_w - T_e) + 0.22\,(T_r - T_e)
	$$

	with

	$$
	T_r - T_e = r\,\frac{\gamma-1}{2}\,M_e^2\,T_e
	$$

	so

	$$
	\frac{T^*}{T_e} = 0.5 + 0.5\frac{T_w}{T_e} + 0.22\,r\,\frac{\gamma-1}{2}\,M_e^2
	$$

	For air (for example \(\gamma=1.4\) and \(r\approx \mathrm{Pr}^{1/3}\approx0.89\)),
	this simplifies to

	$$
	0.22\,r\,\frac{\gamma-1}{2} \approx 0.22\times0.89\times0.2 \approx 0.039
	$$


The local Reynolds number is then corrected as follows:

$$
\mathrm{Re}_x^* = \mathrm{Re}_x\left(\frac{\rho^*}{\rho_e}\right)\left(\frac{\mu_e}{\mu^*}\right)
$$

and the skin-friction estimate based on the Eckert reference temperature method is:

$$
c_f = \frac{0.664}{\sqrt{\mathrm{Re}_x^*}}
$$


The Stanton number is computed with the Reynolds analogy:

$$
C_h = \frac{c_f}{2\,\mathrm{Pr}^{2/3}}
$$

## References

[^1]: Eckert, E.R.G. (1955). *Engineering relations for heat transfer and friction in high-velocity laminar and turbulent boundary-layer flow over surfaces with constant pressure and temperature*. Trans. ASME, 78, 1273-1283.
[^2]: Eckert, E.R.G. (1955). *Engineering relations for friction and heat transfer to surfaces in high velocity flow*.
