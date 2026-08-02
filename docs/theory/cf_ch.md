# Skin Friction and Stanton Number

Laminar and turbulent skin friction coefficient ($c_f$) and Stanton number ($C_h$) estimates for
compressible boundary layers.

The skin-friction coefficient is defined as:

$$
c_f \equiv \frac{\tau_w}{\tfrac{1}{2}\rho_e U_e^2}, 
$$

with $\tau_w$ being the wall shear stress,

$$
\tau_w = \mu_w\left.\frac{\partial u}{\partial y}\right|_w
$$

The Stanton number is defined as:

$$
C_h \equiv \frac{q_w}{\rho_e U_e c_p\,(T_r - T_w)},
$$

with $q_w$ being the wall heat flux, commonly written as

$$
q_w = -k\left.\frac{\partial T}{\partial y}\right|_w.
$$

## Mode and Method Theory Map

### Laminar Estimates

| Method | Theory page |
| --- | --- |
| `blasius` | [Blasius Laminar Method](cf_ch/blasius.md) |
| `eckert_reference` | [Eckert Reference-Temperature Method](cf_ch/eckert_reference.md) |
| `similarity` | [Similarity Method](cf_ch/similarity.md) |

### Turbulent Estimates

- [Compressible to incompressible mapping](cf_ch/turbulent.md)

| Method | Theory page |
| --- | --- |
| `van_driest_ii` | [van Driest II Method](cf_ch/van_driest_ii.md) |
| `spalding_chi` | [Spalding-Chi (1964) Method](cf_ch/spalding_chi_1964.md) |
| `sommer_short` | [Sommer-Short Method](cf_ch/sommer_short.md) |
| `white_christoph` | [White-Christoph Method](cf_ch/white_christoph.md) |

