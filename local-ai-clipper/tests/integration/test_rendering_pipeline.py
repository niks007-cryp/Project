"""
Integration Tests for Video Rendering & Quality Control Pipeline Stage.
"""

import pytest
from pathlib import Path
from clipper.pipeline.ingestion_stage import IngestionStage, IngestionStageInput
from clipper.pipeline.transcription_stage import TranscriptionStage, TranscriptionStageInput
from clipper.pipeline.intelligence_stage import IntelligenceStage, IntelligenceStageInput
from clipper.pipeline.reframing_stage import ReframingStage, ReframingStageInput
from clipper.pipeline.rendering_stage import RenderingStage, RenderingStageInput
from tests.fixtures.media_generator import SyntheticMediaGenerator


def test_rendering_pipeline_execution(manifest_manager, logger, temp_job_dir):
    mp4_path = temp_job_dir / "sample_render.mp4"
    SyntheticMediaGenerator.generate_valid_mp4(mp4_path, duration_sec=15)

    # Full Pipeline Chain: Ingest -> Transcribe -> Intelligence -> Reframing -> Rendering
    ingest_out = IngestionStage(manifest_manager, logger).run(IngestionStageInput(file_path=str(mp4_path)))
    tx_out = TranscriptionStage(manifest_manager, logger).run(TranscriptionStageInput(media_asset=ingest_out.media_asset, use_mock_provider=True))
    intel_out = IntelligenceStage(manifest_manager, logger).run(IntelligenceStageInput(transcript=tx_out.transcript, min_duration_sec=3.0, top_k=1))
    ref_out = ReframingStage(manifest_manager, logger).run(ReframingStageInput(candidate=intel_out.selected_candidates[0], media_asset=ingest_out.media_asset, transcript=tx_out.transcript))

    # Stage 5: Video Rendering
    render_stage = RenderingStage(manifest_manager, logger)
    rnd_inp = RenderingStageInput(
        render_plan=ref_out.render_plan,
        media_asset=ingest_out.media_asset,
        profile_id="preview",  # Fast preview profile for tests
    )

    rnd_out = render_stage.run(rnd_inp)
    assert rnd_out.rendered_asset is not None
    assert Path(rnd_out.rendered_asset.file_path).exists()
    assert rnd_out.rendered_asset.size_bytes > 0
    assert rnd_out.rendered_asset.qc_result.status != "FAILED"
    assert rnd_out.is_idempotent_skip is False

    # Idempotency check
    rnd_out_second = render_stage.run(rnd_inp)
    assert rnd_out_second.is_idempotent_skip is True
