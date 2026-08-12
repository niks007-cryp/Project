"""
Integration Tests for Transcription Pipeline Stage.
"""

import pytest
from pathlib import Path
from clipper.pipeline.ingestion_stage import IngestionStage, IngestionStageInput
from clipper.pipeline.transcription_stage import TranscriptionStage, TranscriptionStageInput
from clipper.infrastructure.asr.base_provider import ASRConfig
from clipper.core.errors import InputError
from tests.fixtures.media_generator import SyntheticMediaGenerator


def test_transcription_pipeline_mock_provider(manifest_manager, logger, temp_job_dir):
    mp4_path = temp_job_dir / "sample.mp4"
    SyntheticMediaGenerator.generate_valid_mp4(mp4_path, duration_sec=10)

    ingest_stage = IngestionStage(manifest_manager, logger)
    ingest_out = ingest_stage.run(IngestionStageInput(file_path=str(mp4_path)))

    tx_stage = TranscriptionStage(manifest_manager, logger)
    tx_inp = TranscriptionStageInput(
        media_asset=ingest_out.media_asset,
        asr_config=ASRConfig(model_name="whisper-tiny", device="cpu"),
        use_mock_provider=True,
    )

    tx_out = tx_stage.run(tx_inp)
    assert tx_out.transcript.transcript_id.startswith("tx_")
    assert len(tx_out.transcript.segments) == 2
    assert Path(tx_out.extracted_audio_path).exists()
    assert tx_out.is_idempotent_skip is False

    # Check manifest checkpoint
    manifest = manifest_manager.load()
    assert manifest.transcript is not None
    assert manifest.stages["transcription"].status == "SUCCEEDED"


def test_transcription_pipeline_idempotency(manifest_manager, logger, temp_job_dir):
    mp4_path = temp_job_dir / "sample_idemp.mp4"
    SyntheticMediaGenerator.generate_valid_mp4(mp4_path, duration_sec=10)

    ingest_stage = IngestionStage(manifest_manager, logger)
    ingest_out = ingest_stage.run(IngestionStageInput(file_path=str(mp4_path)))

    tx_stage = TranscriptionStage(manifest_manager, logger)
    tx_inp = TranscriptionStageInput(
        media_asset=ingest_out.media_asset,
        asr_config=ASRConfig(model_name="whisper-tiny", device="cpu"),
        use_mock_provider=True,
    )

    tx_out1 = tx_stage.run(tx_inp)
    assert tx_out1.is_idempotent_skip is False

    # Second run
    tx_out2 = tx_stage.run(tx_inp)
    assert tx_out2.is_idempotent_skip is True
    assert tx_out2.transcript.transcript_id == tx_out1.transcript.transcript_id


def test_transcription_video_only_raises_input_error(manifest_manager, logger, temp_job_dir):
    vo_path = temp_job_dir / "video_only.mp4"
    SyntheticMediaGenerator.generate_video_only(vo_path, duration_sec=10)

    ingest_stage = IngestionStage(manifest_manager, logger)
    ingest_out = ingest_stage.run(IngestionStageInput(file_path=str(vo_path), require_audio=False))

    tx_stage = TranscriptionStage(manifest_manager, logger)
    with pytest.raises(InputError):
        tx_stage.run(TranscriptionStageInput(media_asset=ingest_out.media_asset, use_mock_provider=True))
