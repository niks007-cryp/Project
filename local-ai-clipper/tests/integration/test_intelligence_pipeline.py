"""
Integration Tests for Content Intelligence Pipeline Stage.
"""

import pytest
from pathlib import Path
from clipper.pipeline.ingestion_stage import IngestionStage, IngestionStageInput
from clipper.pipeline.transcription_stage import TranscriptionStage, TranscriptionStageInput
from clipper.pipeline.intelligence_stage import IntelligenceStage, IntelligenceStageInput
from clipper.core.errors import InputError
from clipper.domain.models import Transcript, ASRProvenance
from tests.fixtures.media_generator import SyntheticMediaGenerator


def test_intelligence_pipeline_execution(manifest_manager, logger, temp_job_dir):
    mp4_path = temp_job_dir / "sample_intel.mp4"
    SyntheticMediaGenerator.generate_valid_mp4(mp4_path, duration_sec=40)

    # Stage 1: Ingestion
    ingest_stage = IngestionStage(manifest_manager, logger)
    ingest_out = ingest_stage.run(IngestionStageInput(file_path=str(mp4_path)))

    # Stage 2: Transcription
    tx_stage = TranscriptionStage(manifest_manager, logger)
    tx_out = tx_stage.run(TranscriptionStageInput(media_asset=ingest_out.media_asset, use_mock_provider=True))

    # Stage 3: Content Intelligence
    intel_stage = IntelligenceStage(manifest_manager, logger)
    intel_inp = IntelligenceStageInput(
        transcript=tx_out.transcript,
        min_duration_sec=3.0,
        max_duration_sec=35.0,
        top_k=2,
    )

    intel_out = intel_stage.run(intel_inp)
    assert len(intel_out.candidates) > 0
    assert len(intel_out.selected_candidates) <= 2
    assert intel_out.is_idempotent_skip is False

    # Idempotency check
    intel_out_second = intel_stage.run(intel_inp)
    assert intel_out_second.is_idempotent_skip is True


def test_empty_transcript_raises_input_error(manifest_manager, logger, temp_job_dir):
    empty_tx = Transcript(
        transcript_id="tx_empty",
        asset_id="asset_empty",
        duration_seconds=10.0,
        segments=[],
        provenance=ASRProvenance(),
    )
    intel_stage = IntelligenceStage(manifest_manager, logger)
    with pytest.raises(InputError):
        intel_stage.run(IntelligenceStageInput(transcript=empty_tx))
