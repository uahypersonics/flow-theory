"""Callbacks for global options in the flow-theory CLI."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
import logging

import typer


# --------------------------------------------------
# version callback
# --------------------------------------------------
def version_callback(value: bool) -> None:
    """Print version and exit when --version is passed."""
    if value:
        # note: __version__ is defined in flow_theory/__init__.py
        from flow_theory import __version__

        typer.echo(f"flow-theory {__version__}")
        raise typer.Exit()


# --------------------------------------------------
# verbose callback
# --------------------------------------------------
def verbose_callback(value: bool) -> None:
    """Configure normal or verbose logging to stderr."""

    # select detailed logging only when verbose output is requested
    log_level = logging.DEBUG if value else logging.INFO
    logger = logging.getLogger("flow-theory")
    logger.setLevel(log_level)
    logger.propagate = False

    # reuse the CLI handler when callbacks run repeatedly in one process
    handler = next(
        (
            existing_handler
            for existing_handler in logger.handlers
            if getattr(existing_handler, "_flow_theory_cli_handler", False)
        ),
        None,
    )
    if handler is None:
        handler = logging.StreamHandler()
        handler._flow_theory_cli_handler = True
        handler.setFormatter(
            logging.Formatter("[%(levelname)-7s] %(funcName)s: %(message)s")
        )
        logger.addHandler(handler)

    handler.setLevel(log_level)
