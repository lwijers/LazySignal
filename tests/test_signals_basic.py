import pytest

from lazysignal import SignalHub, Signal


def test_signal_basic_subscribe_and_emit():
    sig = Signal("test.event")
    received: list[int] = []

    def handler(x: int) -> None:
        received.append(x)

    sig.connect(handler)
    sig.emit(1)
    sig.emit(2)

    assert received == [1, 2]


def test_signal_priority_order():
    sig = Signal("test.priority")
    order: list[str] = []

    def low():
        order.append("low")

    def high():
        order.append("high")

    # low priority first (0), then high priority (10) → high should run first
    sig.connect(low, priority=0)
    sig.connect(high, priority=10)

    sig.emit()

    assert order == ["high", "low"]


def test_signal_once_subscriber_removed_after_emit():
    sig = Signal("test.once")
    calls: list[str] = []

    def once_handler():
        calls.append("once")

    def regular_handler():
        calls.append("regular")

    # Geef de once-handler een hogere priority, zodat hij eerst wordt aangeroepen
    sig.connect(regular_handler, priority=0)
    sig.connect(once_handler, once=True, priority=10)

    sig.emit()   # both should fire: once (prio 10) then regular (prio 0)
    sig.emit()   # only regular should fire

    assert calls == ["once", "regular", "regular"]
    # En intern moet nu alleen de reguliere subscriber overblijven
    assert len(sig) == 1



def test_signal_disconnect():
    sig = Signal("test.disconnect")
    calls: list[int] = []

    def handler(x: int):
        calls.append(x)

    sig.connect(handler)
    sig.emit(1)
    sig.disconnect(handler)
    sig.emit(2)

    assert calls == [1]


def test_signal_emit_args_and_kwargs():
    sig = Signal("test.args")
    received: list[tuple] = []

    def handler(a, b=None):
        received.append((a, b))

    sig.connect(handler)
    sig.emit(1, b=2)

    assert received == [(1, 2)]


def test_signalhub_subscribe_and_emit():
    hub = SignalHub()
    received: list[int] = []

    def handler(x: int):
        received.append(x)

    hub.subscribe("game.score.changed", handler)
    hub.emit("game.score.changed", 10)
    hub.emit("game.score.changed", 20)

    assert received == [10, 20]


def test_signalhub_unsubscribe():
    hub = SignalHub()
    received: list[int] = []

    def handler(x: int):
        received.append(x)

    hub.subscribe("game.score.changed", handler)
    hub.emit("game.score.changed", 1)

    hub.unsubscribe("game.score.changed", handler)
    hub.emit("game.score.changed", 2)

    assert received == [1]


def test_signalhub_emit_nonexistent_signal_is_noop():
    hub = SignalHub()
    # No signals registered yet, should not crash
    hub.emit("nonexistent.event", some_arg=123)

    assert hub.stats()["signal_count"] == 0


def test_signalhub_clear_signal():
    hub = SignalHub()
    calls: list[int] = []

    def handler(x: int):
        calls.append(x)

    hub.subscribe("evt", handler)
    hub.emit("evt", 1)

    hub.clear_signal("evt")
    hub.emit("evt", 2)

    # no extra calls after clear
    assert calls == [1]


def test_signalhub_remove_signal():
    hub = SignalHub()
    calls: list[int] = []

    def handler(x: int):
        calls.append(x)

    hub.subscribe("evt", handler)
    hub.emit("evt", 1)

    hub.remove_signal("evt")
    hub.emit("evt", 2)

    assert calls == [1]
    assert hub.stats()["signal_count"] == 0


def test_signalhub_clear_all():
    hub = SignalHub()

    def h1():
        pass

    def h2():
        pass

    hub.subscribe("a", h1)
    hub.subscribe("b", h2)

    assert hub.stats()["signal_count"] == 2

    hub.clear_all()
    assert hub.stats()["signal_count"] == 0


def test_signalhub_stats_structure():
    hub = SignalHub()

    def h1():
        pass

    def h2():
        pass

    hub.subscribe("a", h1)
    hub.subscribe("a", h2)

    stats = hub.stats()

    assert "signal_count" in stats
    assert "signals" in stats
    assert stats["signal_count"] == 1
    assert stats["signals"]["a"] == 2
