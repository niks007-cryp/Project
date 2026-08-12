"""
Unit Tests for ASR Provider Abstraction & FasterWhisper.
"""

import pytest
from pathlib import Path
from clipper.infrastructure.asr.base_provider import ASRConfig
from clipper.infrastructure.asr.mock_provider import MockASRProvider
from clipper.infrastructure.asr.faster_whisper_provider import FasterWhisperProvider
from clipper.core.errors import ModelError
from tests.fixtures.media_generator import SyntheticMediaGenerator


def test_mock_asr_provider_execution(temp_job_dir):
    audio_path = temp_job_dir / "test_audio.wav"
    audio_path.write_bytes(b"RIFF_DUMMY_PCM_BYTES")

    provider = MockASRProvider()
    config = ASRConfig(device="cpu", compute_type="int8")
    
    res = provider.transcribe(audio_path, config)
    assert res.language_detected == "en"
    assert len(res.segments) == 2
    assert res.segments[0].words[0].word == "Welcome"
    assert res.execution_duration_ms > 0.0


def test_faster_whisper_provider_smoke(temp_job_dir):
    mp4_path = temp_job_dir / "speech_sample.mp4"
    SyntheticMediaGenerator.generate_valid_mp4(mp4_path)

    # Extract PCM WAV using FFmpeg for ASR test
    audio_path = temp_job_dir / "audio.wav"
    from clipper.infrastructure.ffmpeg import SafeFFmpeg
    SafeFFmpeg.run_command(["-i", str(mp4_path), "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", str(audio_path)])

    provider = FasterWhisperProvider()
    config = ASRConfig(model_name="whisper-tiny", device="cpu", compute_type="int8")

    res = provider.transcribe(audio_path, config)
    assert res.language_detected is not None
    assert isinstance(res.segments, list)
    assert res.execution_duration_ms > 0.0


def test_invalid_model_name_raises(temp_job_dir):
    audio_path = temp_job_dir / "test_audio.wav"
    audio_path.write_bytes(b"RIFF_DUMMY_PCM_BYTES")

    provider = FasterWhisperProvider()
    config = ASRConfig(model_name="non_existent_whisper_model_xyz", device="cpu")

    with pytest.raises(ModelError):
        provider.transcribe(audio_path, config)
