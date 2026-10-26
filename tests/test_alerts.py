import pytest

from drowsyalert.pipeline.alerts import AlertManager
from drowsyalert.types import AlertState


def manager_with_player(tmp_path, *, cooldown=5.0, enabled=True, fail=False):
    sound = tmp_path / "alert.wav"
    sound.write_bytes(b"RIFF-test")
    played = []
    stopped = []

    def player(path):
        played.append(path)
        if fail:
            raise RuntimeError("speaker failed")

    manager = AlertManager(
        cooldown,
        enabled=enabled,
        sound=sound,
        player=player,
        stopper=lambda: stopped.append(True),
        available=True,
    )
    return manager, played, stopped


def test_first_alert_sustained_cooldown_and_boundary(tmp_path):
    manager, played, _ = manager_with_player(tmp_path, cooldown=5)
    assert manager.update(AlertState.ALERT, 0)
    assert not manager.update(AlertState.ALERT, 4.999)
    assert manager.update(AlertState.ALERT, 5.0)
    assert len(played) == 2
    assert manager.metadata()["play_count"] == 2
    assert manager.metadata()["alert_active"] is True
    assert manager.metadata()["playing"] is True


def test_recovery_stops_sound_and_cooldown_bounds_realert(tmp_path):
    manager, played, stopped = manager_with_player(tmp_path, cooldown=5)
    assert manager.update(AlertState.ALERT, 0)
    assert not manager.update(AlertState.NORMAL, 1)
    assert stopped == [True]
    assert not manager.update(AlertState.ALERT, 2)
    assert manager.update(AlertState.ALERT, 5)
    assert len(played) == 2


def test_mute_never_calls_player_but_reports_alert_state(tmp_path):
    manager, played, _ = manager_with_player(tmp_path, enabled=False)
    assert not manager.update(AlertState.ALERT, 0)
    status = manager.metadata()
    assert not played
    assert status["enabled"] is False
    assert status["alert_active"] is True
    assert status["playing"] is False
    assert status["play_count"] == 0


def test_missing_sound_is_unavailable_without_changing_detection(tmp_path):
    manager = AlertManager(
        sound=tmp_path / "missing.wav",
        player=lambda _path: pytest.fail("missing sound must not play"),
        stopper=lambda: None,
        available=True,
    )
    assert not manager.update(AlertState.ALERT, 0)
    status = manager.metadata()
    assert status["available"] is False
    assert status["alert_active"] is True
    assert "not found" in status["last_error"].lower()


def test_playback_failure_is_recorded_and_does_not_raise(tmp_path):
    manager, _, _ = manager_with_player(tmp_path, fail=True)
    assert not manager.update(AlertState.ALERT, 0)
    status = manager.metadata()
    assert status["failure_count"] == 1
    assert status["play_count"] == 0
    assert status["available"] is False
    assert status["last_error"] == "speaker failed"


def test_close_stops_active_playback_and_is_idempotent(tmp_path):
    manager, _, stopped = manager_with_player(tmp_path)
    manager.update(AlertState.ALERT, 0)
    manager.close()
    manager.close()
    status = manager.metadata()
    assert stopped == [True]
    assert status["alert_active"] is False
    assert status["playing"] is False


@pytest.mark.parametrize("timestamp", [-1, float("nan"), float("inf")])
def test_invalid_audio_timestamp_is_rejected(tmp_path, timestamp):
    manager, _, _ = manager_with_player(tmp_path)
    with pytest.raises(ValueError, match="timestamp"):
        manager.update(AlertState.ALERT, timestamp)


def test_invalid_cooldown_is_rejected():
    with pytest.raises(ValueError, match="cooldown"):
        AlertManager(cooldown=0)
