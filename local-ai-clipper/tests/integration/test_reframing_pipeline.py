"""
Integration Tests for Reframing & RenderPlan Pipeline Stage.
"""

import pytest
from clipper.pipeline.ingestion_stage import IngestionStage, IngestionStageInput
from clipper.pipeline.transcription_stage import TranscriptionStage, TranscriptionStageInput
from clipper.pipeline.intelligence_stage import IntelligenceStage, IntelligenceStageInput
from clipper.pipeline.reframing_stage import ReframingStage, ReframingStageInput
from tests.fixtures.media_generator import SyntheticMediaGenerator


def test_reframing_pipeline_execution(manifest_manager, logger, temp_job_dir):
    mp4_path = temp_job_dir / "sample_reframing.mp4"
    SyntheticMediaGenerator.generate_valid_mp4(mp4_path, duration_sec=40)

    # Ingestion
    ingest_out = IngestionStage(manifest_manager, logger).run(IngestionStageInput(file_path=str(mp4_path)))
    # Transcription
    tx_out = TranscriptionStage(manifest_manager, logger).run(
        TranscriptionStageInput(media_asset=ingest_out.media_asset, use_mock_provider=True)
    )
    # Intelligence
    intel_out = IntelligenceStage(manifest_manager, logger).run(
        IntelligenceStageInput(transcript=tx_out.transcript, min_duration_sec=3.0, top_k=1)
    )

    selected_cand = intel_out.selected_candidates[0]

    # Reframing & RenderPlan
    reframing_stage = ReframingStage(manifest_manager, logger)
    ref_inp = ReframingStageInput(
        candidate=selected_cand,
        media_asset=ingest_out.media_asset,
        transcript=tx_out.transcript,
    )

    ref_out = reframing_stage.run(ref_inp)
    assert ref_out.render_plan is not None
    assert ref_out.render_plan.plan_id == f"plan_{selected_cand.candidate_id}"
    assert len(ref_out.render_plan.crop_keyframes) > 0
    assert len(ref_out.render_plan.caption_segments) > 0
    assert ref_out.is_idempotent_skip is False

    # Idempotency check
    ref_out_second = reframing_stage.run(ref_inp)
    assert ref_out_second.is_idempotent_skip is True
