"""Audio is a side effect of an alert event; it never blocks the frame loop."""

import logging
import sys
from importlib.resources import files

from drowsyalert.types import AlertState

LOGGER = logging.getLogger(__name__)


class AlertManager:
    def __init__(self, cooldown: float = 5, enabled: bool = True, sound=None):
        self.cooldown, self.enabled = cooldown, enabled
        self.sound = sound or files("drowsyalert").joinpath("assets/alert.wav")
        self.last_played = None
        self.active = False
        self.available = sys.platform == "win32"

    def update(self, state: AlertState, timestamp: float) -> bool:
        if state != AlertState.ALERT:
            if self.active:
                self.stop()
            self.active = False
            return False
        due = self.last_played is None or timestamp - self.last_played >= self.cooldown
        self.active = True
        if not self.enabled or not due:
            return False
        self.last_played = timestamp
        if self.available:
            import winsound

            try:
                winsound.PlaySound(str(self.sound), winsound.SND_FILENAME | winsound.SND_ASYNC)
            except RuntimeError:
                LOGGER.warning("Unable to play alert sound", exc_info=True)
        return True

    def stop(self):
        if self.available and self.enabled:
            import winsound

            winsound.PlaySound(None, 0)

    def close(self):
        self.stop()
