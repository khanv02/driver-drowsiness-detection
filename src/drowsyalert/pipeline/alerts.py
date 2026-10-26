"""Bounded, observable audio side effects that never block decision logic."""

import logging
import math
import sys
from importlib.resources import files

from drowsyalert.types import AlertState

LOGGER = logging.getLogger(__name__)


def _windows_play(sound) -> None:
    import winsound

    winsound.PlaySound(str(sound), winsound.SND_FILENAME | winsound.SND_ASYNC)


def _windows_stop() -> None:
    import winsound

    winsound.PlaySound(None, 0)


class AlertManager:
    def __init__(
        self,
        cooldown: float = 5,
        enabled: bool = True,
        sound=None,
        *,
        player=None,
        stopper=None,
        available: bool | None = None,
    ):
        if not math.isfinite(cooldown) or cooldown <= 0:
            raise ValueError("Audio cooldown must be finite and greater than zero")
        self.cooldown = cooldown
        self.enabled = enabled
        self.sound = sound or files("drowsyalert").joinpath("assets/alert.wav")
        self._player = player or _windows_play
        self._stopper = stopper or _windows_stop
        platform_available = sys.platform == "win32" if available is None else available
        sound_available = self.sound.is_file()
        self.available = bool(platform_available and sound_available)
        self.last_error = None
        if not sound_available:
            self.last_error = f"Alert sound not found: {self.sound}"
        elif not platform_available:
            self.last_error = "Audio playback is unavailable on this platform"
        self.last_played = None
        self.alert_active = False
        self.playing = False
        self.play_count = 0
        self.failure_count = 0

    def update(self, state: AlertState, timestamp: float) -> bool:
        if not math.isfinite(timestamp) or timestamp < 0:
            raise ValueError("Audio timestamp must be finite and nonnegative")
        if state != AlertState.ALERT:
            self.alert_active = False
            self.stop()
            return False

        self.alert_active = True
        due = self.last_played is None or timestamp - self.last_played >= self.cooldown
        if not self.enabled or not self.available or not due:
            return False
        try:
            self._player(self.sound)
        except (OSError, RuntimeError) as error:
            self.failure_count += 1
            self.last_error = str(error)
            self.available = False
            self.playing = False
            LOGGER.warning("Unable to play alert sound", exc_info=True)
            return False
        self.last_played = timestamp
        self.play_count += 1
        self.playing = True
        return True

    def stop(self) -> None:
        if not self.playing:
            return
        try:
            self._stopper()
        except (OSError, RuntimeError) as error:
            self.failure_count += 1
            self.last_error = str(error)
            LOGGER.warning("Unable to stop alert sound", exc_info=True)
        finally:
            self.playing = False

    def close(self) -> None:
        self.stop()
        self.alert_active = False

    def metadata(self) -> dict:
        return {
            "enabled": self.enabled,
            "available": self.available,
            "alert_active": self.alert_active,
            "playing": self.playing,
            "play_count": self.play_count,
            "failure_count": self.failure_count,
            "last_error": self.last_error,
            "cooldown_seconds": self.cooldown,
            "sound": str(self.sound),
        }
