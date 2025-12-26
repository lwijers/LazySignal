from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Any, List

import pygame
from lazysignal import SignalHub


# --------------------------------------------------------------------
# Simple UI Button that emits a signal on click
# --------------------------------------------------------------------
@dataclass
class Button:
    rect: pygame.Rect
    label: str
    hub: SignalHub
    signal_name: str = "ui.button.clicked"

    is_hovered: bool = False

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                # Emit a signal with some payload
                self.hub.emit(self.signal_name, button=self, label=self.label)

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        base_color = (60, 80, 120)
        hover_color = (90, 120, 170)
        click_color = (140, 180, 220) if self.is_hovered else None

        color = hover_color if self.is_hovered else base_color
        if click_color is not None and pygame.mouse.get_pressed()[0] and self.is_hovered:
            color = click_color

        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, (20, 20, 30), self.rect, width=2, border_radius=8)

        text_surf = font.render(self.label, True, (230, 230, 240))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)


def draw_signal_overview(
    surface: pygame.Surface,
    hub: SignalHub,
    font: pygame.font.Font,
    x: int,
    y: int,
) -> None:
    """
    Draw a simple panel listing:
      - which signals exist
      - which handlers are subscribed
    """
    header = font.render("Signals & subscribers:", True, (180, 180, 200))
    surface.blit(header, (x, y))
    y += 22

    # For this demo we peek into the hub internals.
    for name, sig in hub._signals.items():  # type: ignore[attr-defined]
        handler_names: List[str] = []
        for cb in sig.subscribers():
            handler_names.append(getattr(cb, "__name__", repr(cb)))

        text = f"- {name}: {', '.join(handler_names) or '(no subscribers)'}"
        line_surf = font.render(text, True, (200, 200, 220))
        surface.blit(line_surf, (x, y))
        y += 18


def draw_event_log(
    surface: pygame.Surface,
    log_lines: List[str],
    font: pygame.font.Font,
    x: int,
    y: int,
    max_lines: int = 7,
) -> None:
    """
    Draw a small event log panel.
    """
    header = font.render("Event log:", True, (180, 180, 200))
    surface.blit(header, (x, y))
    y += 20

    # Show only the last max_lines lines
    for line in log_lines[-max_lines:]:
        line_surf = font.render(line, True, (210, 210, 230))
        surface.blit(line_surf, (x, y))
        y += 16


# --------------------------------------------------------------------
# Main demo
# --------------------------------------------------------------------
def main() -> None:
    pygame.init()

    screen_width, screen_height = 900, 540
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("LazySignals Pygame Demo")

    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 22)
    small_font = pygame.font.SysFont("consolas", 16)

    hub = SignalHub()

    # ----------------------------------------------------------------
    # Game state
    # ----------------------------------------------------------------
    health = {"current": 100, "max": 100}
    last_message: List[str] = ["Click a button to emit signals."]
    event_log: List[str] = []

    def add_log(line: str) -> None:
        event_log.append(line)

    # ----------------------------------------------------------------
    # Signal handlers
    # ----------------------------------------------------------------
    def on_button_clicked(button: Button, label: str) -> None:
        # Log button clicks into the in-game event log
        add_log(f"[ui.button.clicked] {label!r}")

        if "Take" in label:
            hub.emit("game.player.damage", amount=10, source=label)
        elif "Heal" in label:
            new_val = min(health["max"], health["current"] + 10)
            delta = new_val - health["current"]
            health["current"] = new_val
            if delta > 0:
                hub.emit("ui.notify", f"+{delta} HP (healed)")
            else:
                hub.emit("ui.notify", "HP already full")

    def on_player_damage(amount: int, source: str) -> None:
        health["current"] = max(0, health["current"] - amount)
        hub.emit("ui.notify", f"-{amount} HP from {source}")
        add_log(f"[game.player.damage] -{amount} HP from {source}")

    def on_notify(msg: str) -> None:
        last_message[0] = msg
        add_log(f"[ui.notify] {msg}")

    # Subscribe handlers to signals
    hub.subscribe("ui.button.clicked", on_button_clicked, priority=10)
    hub.subscribe("game.player.damage", on_player_damage)
    hub.subscribe("ui.notify", on_notify)

    # ----------------------------------------------------------------
    # Create button instances
    # ----------------------------------------------------------------
    damage_button = Button(
        rect=pygame.Rect(50, 80, 220, 60),
        label="Take 10 damage",
        hub=hub,
    )

    heal_button = Button(
        rect=pygame.Rect(50, 160, 220, 60),
        label="Heal 10 HP",
        hub=hub,
    )

    running = True

    while running:
        dt = clock.tick(60) / 1000.0  # noqa: F841 (we don't use dt here)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                damage_button.handle_event(event)
                heal_button.handle_event(event)

        # ----------------------------------------------------------------
        # Draw
        # ----------------------------------------------------------------
        screen.fill((15, 18, 30))

        # Title
        title_surf = font.render("LazySignals + Pygame Demo", True, (230, 230, 240))
        screen.blit(title_surf, (50, 20))

        # Buttons
        damage_button.draw(screen, font)
        heal_button.draw(screen, font)

        # Health bar background
        bar_x, bar_y, bar_w, bar_h = 50, 260, 300, 28
        pygame.draw.rect(screen, (40, 40, 60), (bar_x, bar_y, bar_w, bar_h), border_radius=6)

        # Health bar fill
        ratio = health["current"] / health["max"]
        fill_w = int(bar_w * ratio)
        pygame.draw.rect(
            screen,
            (140, 50, 60),
            (bar_x, bar_y, fill_w, bar_h),
            border_radius=6,
        )

        hp_text = small_font.render(
            f"HP: {health['current']} / {health['max']}",
            True,
            (230, 230, 240),
        )
        screen.blit(hp_text, (bar_x + 8, bar_y + 4))

        # Message line from ui.notify
        msg_label = small_font.render("Last message:", True, (180, 180, 190))
        screen.blit(msg_label, (50, 310))

        msg_text = small_font.render(last_message[0], True, (220, 220, 230))
        screen.blit(msg_text, (50, 332))

        # Signals & subscribers panel (right side)
        draw_signal_overview(screen, hub, small_font, x=420, y=80)

        # Event log panel (bottom right)
        draw_event_log(screen, event_log, small_font, x=420, y=260)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
