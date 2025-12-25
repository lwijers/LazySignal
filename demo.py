from lazysignal import SignalHub

hub = SignalHub()


def on_button_clicked(button_id: int):
    print(f"Button {button_id} clicked!")


def on_button_clicked_once(button_id: int):
    print(f"(Once) Button {button_id} clicked!")


# subscribe
unsubscribe = hub.subscribe("ui.button.clicked", on_button_clicked)
hub.subscribe("ui.button.clicked", on_button_clicked_once, once=True, priority=10)

# emit 1
hub.emit("ui.button.clicked", button_id=1)

# emit 2
hub.emit("ui.button.clicked", button_id=2)

# unsubscribe persistent handler
unsubscribe()

# emit 3
hub.emit("ui.button.clicked", button_id=3)
