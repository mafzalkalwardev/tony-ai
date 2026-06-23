from pathlib import Path

from tony.tools.screen_recorder import ScreenRecorder


def test_screen_recorder_uses_local_output_dir(tmp_path):
    recorder = ScreenRecorder(output_dir=tmp_path)

    assert recorder.output_dir == tmp_path
    assert recorder.output_dir.exists()


def test_screen_recorder_stop_without_start_is_safe(tmp_path):
    recorder = ScreenRecorder(output_dir=tmp_path)

    assert "No screen recording" in recorder.stop_recording()
