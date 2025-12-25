"""
LazySignals - a tiny, reusable signal / pub-sub library.

Public API:
    - Signal
    - SignalHub
"""

from .core import Signal, SignalHub

__all__ = ["Signal", "SignalHub"]
