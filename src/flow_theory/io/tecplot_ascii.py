"""Tecplot ASCII writer for 1D ordered POINT zones.

Use :class:`TecplotFile` to open a file once, then write one or more zones
with a shared variable list. The convenience function :func:`write_tecplot`
writes a single zone.
"""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import numpy as np


# --------------------------------------------------
# Tecplot file writer
# --------------------------------------------------
class TecplotFile:
    """Write one or more 1D Tecplot ASCII POINT zones to a file.

    The file is opened lazily and can be managed explicitly or with a
    context manager. Garbage collection is not relied upon for correctness;
    ``with TecplotFile(...) as tecplot:`` is the intended pattern.
    """

    def __init__(self, path: str | Path, title: str, variables: Sequence[str]) -> None:
        self.path = Path(path)
        self.title = str(title)
        self.variables = [str(name) for name in variables]
        self._stream = None
        self._header_written = False

    def __enter__(self) -> TecplotFile:
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback) -> bool:
        self.close()
        return False

    def __del__(self) -> None:
        # best-effort fallback; context manager use is still preferred
        self.close()

    def open(self) -> None:
        """Open the underlying file if it is not already open."""

        if self._stream is None:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self._stream = self.path.open("w", encoding="utf-8")

    def close(self) -> None:
        """Close the underlying file if it is open."""

        if self._stream is not None:
            self._stream.close()
            self._stream = None

    def write_zone(self, zone_name: str, values: Sequence[Sequence[float]] | np.ndarray) -> None:
        """Write one 1D POINT zone from a matrix of values.

        Args:
            zone_name: Tecplot zone name.
            values: Matrix of shape (n_rows, n_vars) or a column-major matrix
                of shape (n_vars, n_rows). A 1D array is accepted only when the
                file has a single variable.
        """

        self.open()
        matrix = self._normalize_matrix(values)
        n_rows, n_vars = matrix.shape

        if not self._header_written:
            self._write_header()

        self._stream.write(f'ZONE T="{zone_name}", I={n_rows}, DATAPACKING=POINT\n')
        for row_values in matrix:
            row_text = " ".join(f"{value:.8e}" for value in row_values)
            self._stream.write(f"{row_text}\n")

    def _write_header(self) -> None:
        """Write the Tecplot title and variable header once."""

        assert self._stream is not None
        self._stream.write(f'TITLE = "{self.title}"\n')
        variables_str = " ".join(f'"{name}"' for name in self.variables)
        self._stream.write(f"VARIABLES = {variables_str}\n")
        self._header_written = True

    def _normalize_matrix(
        self,
        values: Sequence[Sequence[float]] | np.ndarray,
    ) -> np.ndarray:
        """Normalize input values to a 2D row-major matrix."""

        matrix = np.asarray(values, dtype=float)

        if matrix.ndim == 1:
            if len(self.variables) != 1:
                raise ValueError("1D values are only valid when there is exactly one variable")
            return matrix.reshape(-1, 1)

        if matrix.ndim != 2:
            raise ValueError("Tecplot values must be a 1D or 2D array-like object")

        n_vars = len(self.variables)
        if matrix.shape[1] == n_vars:
            return matrix
        if matrix.shape[0] == n_vars:
            return matrix.T

        raise ValueError(
            f"matrix shape {matrix.shape} does not match {n_vars} variables"
        )


# --------------------------------------------------
# public API
# --------------------------------------------------
def write_tecplot(
    path: str | Path,
    title: str,
    variables: Sequence[str],
    zone_name: str,
    values: Sequence[Sequence[float]] | np.ndarray,
) -> Path:
    """Write a single Tecplot 1D zone to disk.

    Args:
        path: Output Tecplot ASCII file path.
        title: Tecplot file title.
        variables: Variable names, in order.
        zone_name: Name of the zone written.
        values: Matrix of values, shape (n_rows, n_vars) or (n_vars, n_rows).

    Returns:
        Resolved output path.
    """

    with TecplotFile(path, title=title, variables=variables) as tecplot_file:
        tecplot_file.write_zone(zone_name, values)

    return Path(path)


