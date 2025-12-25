# LazySignals

**LazySignals** is a tiny, dependency-free **signal / pub-sub library** for Python.

It’s designed to be:

- Simple enough to read in one sitting
- Powerful enough to drive UI events, gameplay events, and decoupled systems
- Easy to integrate into existing engines (like an ECS or UI toolkit)

Typical use cases:

- UI: `"ui.button.clicked"`, `"ui.window.closed"`
- Gameplay: `"game.fish.spawned"`, `"game.enemy.killed"`
- Tools / debug: `"debug.value.changed"`

---

## ✨ Features

- **Named signals** (string-based channels, e.g. `"ui.button.clicked"`)
- **Central hub**: `SignalHub` manages all signals
- **Subscriptions with priority**
  - Higher `priority` = callback runs earlier
- **One-shot subscribers**
  - `once=True` → callback is automatically unsubscribed after first emit
- **Safe emissions**
  - Emitting a non-existent signal is a no-op
  - Errors in callbacks don’t break the hub
- **No dependencies**
  - Pure Python, works anywhere

---

## 📦 Installation

### Local development (editable)

Clone the repo and install in editable mode:

```bash
git clone https://github.com/lwijers/LazySignal.git
cd LazySignal
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e .
Now you can use it in your own projects (within this venv):

python
Copy code
from lazysignals import SignalHub
🧠 Core Concepts
Signal
Represents a single event channel with subscribers.

python
Copy code
from lazysignals import Signal

sig = Signal("ui.button.clicked")

def on_click(button_id: int):
    print("Clicked:", button_id)

# subscribe
sig.connect(on_click)

# emit
sig.emit(button_id=42)
Features:

connect(callback, priority=0, once=False)

disconnect(callback)

emit(*args, **kwargs)

clear() – remove all subscribers

Iteration and len(signal) for debugging

SignalHub
A central registry for all signals.

python
Copy code
from lazysignals import SignalHub

hub = SignalHub()

def on_score_changed(score: int):
    print("Score:", score)

# Subscribe to a named signal
unsubscribe = hub.subscribe("game.score.changed", on_score_changed)

# Emit it
hub.emit("game.score.changed", 10)
hub.emit("game.score.changed", 20)

# Stop listening
unsubscribe()
hub.emit("game.score.changed", 30)  # no output
Key methods:

signal(name) -> Signal – get/create a signal

subscribe(name, callback, priority=0, once=False)

unsubscribe(name, callback)

emit(name, *args, **kwargs)

clear_signal(name)

remove_signal(name)

clear_all()

stats() – simple debug info

🧪 Running Tests
LazySignals comes with a small test suite under tests/.

To run the tests:

bash
Copy code
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
pytest -q
🗺 Project Structure
text
Copy code
LazySignal/
  lazysignals/
    __init__.py
    core.py
  tests/
    test_signals_basic.py
  pyproject.toml
  requirements.txt
  README.md