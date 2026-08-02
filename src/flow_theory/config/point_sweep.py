"""Helpers for resolving point-sweep specs into 1D numeric arrays."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

import math

import numpy as np


# --------------------------------------------------
# public helpers
# --------------------------------------------------
def point_sweep(spec: object, key_name: str) -> np.ndarray:
    """Turn a scalar or sweep specification into a 1D point array.

    Supported forms:
    - 1.0 -> single point
    - [xs, xe, nx] -> linear sweep with count
    - [xs, xe, dx] -> linear sweep with spacing

    Args:
        spec: Scalar or item sequence describing the sweep.
        key_name: Config key name used in error messages.

    Returns:
        1D numpy array of point values.

    Raises:
        ValueError: If the spec is invalid.
    """

    # spec was not provided -> cannot generate sweep
    if spec is None:
        raise ValueError(f"Missing required key: {key_name}")

    # build the final value array and return once at the end
    vals: np.ndarray

    # spec is a scalar (int or float) -> single point
    if isinstance(spec, (int, float)):
        value = float(spec)

        # ensure that the single point is non-negative
        if value < 0.0:
            raise ValueError(f"{key_name} must be non-negative")

        # convert to a 1D array for consistency
        vals = np.asarray([value], dtype=float)

    # spec is not scalar -> must be a 3-item sequence
    else:
        # validate that the spec is a list or tuple
        if not isinstance(spec, (list, tuple)):
            raise ValueError(
                f"Invalid {key_name} type. Use scalar value, [xs, xe, nx], or [xs, xe, dx]"
            )

        # validate that the spec has exactly 3 entries
        if len(spec) != 3:
            raise ValueError(f"{key_name} list must have exactly 3 entries: [xs, xe, nx] or [xs, xe, dx]")

        # unpack the 3-item spec and convert to floats

        # first item is start point
        try:
            start = float(spec[0])
        except (TypeError, ValueError):
            raise ValueError(f"{key_name}[0] (start) must be a numeric value")

        # second item is end point
        try:
            end = float(spec[1])
        except (TypeError, ValueError):
            raise ValueError(f"{key_name}[1] (end) must be a numeric value")

        # third item is either count or spacing (sweep argument)
        try:
            sweep_arg = float(spec[2])
        except (TypeError, ValueError):
            raise ValueError(f"{key_name}[2] must be a numeric value")

        # validate the start being non-negative
        if start < 0.0:
            raise ValueError(f"{key_name}[0] (start) must be non-negative")

        # validate the end being greater than the start value
        if end <= start:
            raise ValueError(f"{key_name}[1] (end) must be greater than start")

        # validate the third item being positive
        if sweep_arg <= 0.0:
            raise ValueError(f"{key_name}[2] must be positive")

        # round the sweep argument to the nearest integer to determine if it is a count or spacing
        sweep_arg_rounded = int(round(sweep_arg))

        # if the sweep argument is close to an integer, treat it as a count (it likely is an integer)
        if abs(sweep_arg - sweep_arg_rounded) < 1e-12:

            # if the sweep argument is less than 2, it cannot be a valid count
            if sweep_arg_rounded < 2:
                raise ValueError(f"{key_name} interpreted as [start, stop, count], and count must be at least 2")

            # generate a linear sweep with the specified count
            vals = np.linspace(start, end, sweep_arg_rounded, dtype=float)
        else:
            # sweep arg is not close to an integer -> treat it as a spacing value
            step = sweep_arg

            # compute the number of points that fit in the range [start, end] with the given step size (floor division)
            count = int(math.floor((end - start) / step))

            # generate the linear sweep with the specified spacing
            vals = start + step * np.arange(count + 1, dtype=float)

            # ensure that the end point is included in the array if it is not already present
            if not np.isclose(vals[-1], end, rtol=0.0, atol=max(1e-14, 1e-12 * end)):
                vals = np.append(vals, end)

    return vals
