# Entropy-Layer Swallowing

The bow shock at a blunt nose is nearly normal near the stagnation point and
becomes progressively more oblique away from the axis. Fluid that crosses
the strong, nearly-normal part of the shock picks up much more entropy than
fluid crossing the weaker, oblique part further out -- this creates a layer
of non-uniform entropy (the "entropy layer") that wraps around the body
downstream of the nose. The growing viscous boundary layer eventually
becomes thicker than this entropy layer, at which point the entropy layer
is said to be "swallowed" and the boundary layer sees a nearly uniform edge
state, as on a sharp-nosed body.

## Swallowing Distance

`flow_theory.entropy_swallowing` defines the swallowing distance $x_\mathrm{sw}$
as the streamwise location where the boundary-layer thickness
$\delta_\mathrm{BL}(x)$ equals the entropy-layer thickness
$\delta_\mathrm{EL}(x)$, and solves for it by root-finding.

**Boundary-layer thickness** uses the compressible laminar flat-plate
estimate (Blasius scaling $\delta_{99}/x = 5/\sqrt{\mathrm{Re}_x}$),
corrected for compressibility using the same Eckert (1955) reference
temperature ratio used in [`cf_ch`](cf_ch.md):

$$\delta_\mathrm{BL}(x) = 5\,\frac{x}{\sqrt{\mathrm{Re}_x}}\,\frac{T^*}{T_e}$$

**Entropy-layer thickness** uses the classical blast-wave/entropy-layer
growth estimate for axisymmetric bodies[^lees_1955], which grows as
$(x/R_\mathrm{nose})^{1/3}$, scaled by the normal-shock density
ratio[^anderson_2003] at $M_e$ as a proxy for shock strength:

$$\delta_\mathrm{EL}(x) = R_\mathrm{nose}\left(\frac{x}{R_\mathrm{nose}}\right)^{1/3}\epsilon, \qquad \epsilon = \frac{(\gamma-1)M_e^2+2}{(\gamma+1)M_e^2}$$

## Scope and Limitations

Rotta's (1966)[^rotta_1966] full closed-form correlation requires the
sharp-cone Taylor-Maccoll inviscid solution (cone surface Mach number and
pressure) and the Lees similarity edge stream-function value, which are out
of scope here -- `flow_theory` takes only edge conditions ($M_e$, $T_w/T_0$)
and nose radius as inputs. The physical picture
($\delta_\mathrm{BL} = \delta_\mathrm{EL}$ at $x_\mathrm{sw}$) and the
qualitative Reynolds-number and bluntness trends match Rotta (1966) and
Stetson (1983)[^stetson_1983]; exact numerical agreement with either paper's
tabulated results is not expected because of this simplification -- see the
[Rotta (1966) validation case](../vnv/validation/rotta_1966_blunt_cone_swallowing/index.md)
for a documented, loose-tolerance comparison.

[^lees_1955]: Lees, L. (1955). *Hypersonic flow*. 5th International Aeronautical Conference, Los Angeles, pp. 241-276.
[^anderson_2003]: Anderson, J.D. (2003). *Modern Compressible Flow*, 3rd ed., eq. 3.53.
[^rotta_1966]: Rotta, N.R. (1966). *Effects of nose bluntness on the boundary layer characteristics of conical bodies at hypersonic speeds*. NYU-AA-66-66.
[^stetson_1983]: Stetson, K.F. (1983). *Nosetip bluntness effects on cone frustum boundary layer transition in hypersonic flow*. AIAA 83-1763.
