from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Any, Dict, List, Tuple, Iterable, Optional

Callback = Callable[..., None]


@dataclass
class _Subscriber:
    """Internal record for a single subscriber to a Signal."""
    callback: Callback
    priority: int = 0
    once: bool = False


class Signal:
    """
    A single signal (event channel) with a list of subscribers.

    Typical usage (usually via SignalHub):

        signal = Signal("ui.button.clicked")
        unsub = signal.connect(on_click, priority=10)
        signal.emit(button_id=5)

    Subscribers:

        - Are called in descending order of priority (higher first).
        - If 'once=True', they are automatically disconnected after first emit.
    """

    __slots__ = ("name", "_subscribers")

    def __init__(self, name: str) -> None:
        self.name = name
        self._subscribers: List[_Subscriber] = []

    # ------------------------------------------------------------------
    # Subscription management
    # ------------------------------------------------------------------

    def connect(self, callback: Callback, *, priority: int = 0, once: bool = False) -> Callable[[], None]:
        """
        Subscribe a callback to this signal.

        Args:
            callback: Function called when the signal is emitted.
            priority: Higher priority callbacks are called first.
            once: If True, the callback is removed after first emit.

        Returns:
            A callable 'unsubscribe()' that removes this subscription.
        """
        sub = _Subscriber(callback=callback, priority=priority, once=once)
        self._subscribers.append(sub)
        # Keep list sorted by priority (high to low)
        self._subscribers.sort(key=lambda s: s.priority, reverse=True)

        def unsubscribe() -> None:
            self.disconnect(callback)

        return unsubscribe

    def disconnect(self, callback: Callback) -> None:
        """Remove a callback subscription from this signal."""
        self._subscribers = [
            s for s in self._subscribers
            if s.callback is not callback
        ]

    def clear(self) -> None:
        """Remove all subscribers from this signal."""
        self._subscribers.clear()

    # ------------------------------------------------------------------
    # Emitting
    # ------------------------------------------------------------------

    def emit(self, *args: Any, **kwargs: Any) -> None:
        """
        Emit this signal: call all subscribers with the given arguments.

        Subscribers marked 'once=True' are removed after this emit.
        """
        if not self._subscribers:
            return

        # Work on a snapshot so a callback can subscribe/unsubscribe safely.
        subs_snapshot = list(self._subscribers)
        to_remove: List[Callback] = []

        for sub in subs_snapshot:
            try:
                sub.callback(*args, **kwargs)
            except Exception as exc:  # we don't re-raise by default
                # You can later hook in a logging strategy here.
                print(f"[LazySignals] Error in callback for '{self.name}': {exc}")
            if sub.once:
                to_remove.append(sub.callback)

        # Remove once-subscribers
        if to_remove:
            for cb in to_remove:
                self.disconnect(cb)

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def subscribers(self) -> Iterable[Callback]:
        """Iterate over subscribed callbacks (for debugging / tools)."""
        return (s.callback for s in self._subscribers)

    def __len__(self) -> int:
        return len(self._subscribers)

    def __repr__(self) -> str:
        return f"<Signal name={self.name!r} subscribers={len(self)}>"


class SignalHub:
    """
    A central registry of named signals.

    This is the usual entrypoint for an application or engine:

        hub = SignalHub()
        hub.subscribe("game.fish.spawned", on_fish_spawn)
        hub.emit("game.fish.spawned", species="goldfish")

    Signals are created lazily on first use.
    """

    def __init__(self) -> None:
        self._signals: Dict[str, Signal] = {}

    # ------------------------------------------------------------------
    # Access to signals
    # ------------------------------------------------------------------

    def signal(self, name: str) -> Signal:
        """
        Get a signal by name, creating it if it does not exist yet.
        """
        sig = self._signals.get(name)
        if sig is None:
            sig = Signal(name)
            self._signals[name] = sig
        return sig

    def has_signal(self, name: str) -> bool:
        """Return True if a signal with this name exists."""
        return name in self._signals

    def all_signals(self) -> Iterable[Tuple[str, Signal]]:
        """Iterate over all (name, Signal) pairs."""
        return self._signals.items()

    # ------------------------------------------------------------------
    # High-level convenience API
    # ------------------------------------------------------------------

    def subscribe(
            self,
            name: str,
            callback: Callback,
            *,
            priority: int = 0,
            once: bool = False,
    ) -> Callable[[], None]:
        """
        Subscribe to a named signal.

        Args:
            name: Signal name, e.g. 'ui.button.clicked'.
            callback: Function to call.
            priority: Higher priority = earlier call order.
            once: If True, remove after first emit.

        Returns:
            An 'unsubscribe()' function.
        """
        sig = self.signal(name)
        return sig.connect(callback, priority=priority, once=once)

    def unsubscribe(self, name: str, callback: Callback) -> None:
        """
        Unsubscribe a callback from the named signal.
        Does nothing if the signal does not exist (safe to call).
        """
        sig = self._signals.get(name)
        if sig is not None:
            sig.disconnect(callback)

    def emit(self, name: str, *args: Any, **kwargs: Any) -> None:
        """
        Emit an event on a named signal.

        If the signal does not exist, this is a no-op.
        """
        sig = self._signals.get(name)
        if sig is not None:
            sig.emit(*args, **kwargs)

    def clear_signal(self, name: str) -> None:
        """
        Remove all subscribers from a named signal.
        The signal object itself remains.
        """
        sig = self._signals.get(name)
        if sig is not None:
            sig.clear()

    def remove_signal(self, name: str) -> None:
        """
        Completely remove the named signal from the hub.
        """
        self._signals.pop(name, None)

    def clear_all(self) -> None:
        """
        Remove all signals and their subscribers.
        """
        self._signals.clear()

    # ------------------------------------------------------------------
    # Introspection / debug
    # ------------------------------------------------------------------

    def stats(self) -> Dict[str, Any]:
        """
        Return simple diagnostic information about this hub.
        """
        return {
            "signal_count": len(self._signals),
            "signals": {
                name: len(sig)
                for name, sig in self._signals.items()
            },
        }

    def __repr__(self) -> str:
        return f"<SignalHub signals={len(self._signals)}>"
