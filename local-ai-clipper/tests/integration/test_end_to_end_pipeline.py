"""
Integration Tests for Floor 8 Central Pipeline Orchestrator & End-to-End Execution.
"""

import pytest
import tempfile
from pathlib import Path
from clipper.pipeline.orchestrator import PipelineOrchestrator
from clipper.core.state import JobState
from tests.fixtures.media_generator import SyntheticMediaGenerator


def test_end_to_end_pipeline_execution():
    """Full 5-stage pipeline executes successfully on synthetic 15s media."""
    with tempfile.TemporaryDirectory() as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        media_file = tmp_dir / "e2e_input.mp4"
        SyntheticMediaGenerator.generate_valid_mp4(media_file, duration_sec=15)

        orchestrator = PipelineOrchestrator()
        result = orchestrator.run_pipeline(
            source_file_path=str(media_file),
            job_id="test_job_e2e_01",
            options={"mock_asr": True, "profile": "preview", "top_k": 2},
        )

        assert result["status"] == JobState.SUCCEEDED.value
        assert result["media_asset"]["filename"] == "e2e_input.mp4"
        assert result["transcript"] is not None
        assert len(result["candidates"]) > 0
        assert result["render_plan"] is not None
        assert result["rendered_asset"] is not None
        assert result["rendered_asset"]["qc_result"]["status"] in ["QCStatus.PASSED", "PASSED"]


def test_pipeline_checkpoint_resumability():
    """Re-invoking run_pipeline on a completed job hits all checkpoints without re-executing."""
    with tempfile.TemporaryDirectory() as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        media_file = tmp_dir / "resumable.mp4"
        SyntheticMediaGenerator.generate_valid_mp4(media_file, duration_sec=10)

        orchestrator = PipelineOrchestrator()
        res1 = orchestrator.run_pipeline(
            str(media_file), job_id="job_resume_01", options={"mock_asr": True}
        )
        assert res1["status"] == JobState.SUCCEEDED.value

        # Re-run: all stages should be checkpointed
        res2 = orchestrator.resume_pipeline("job_resume_01", options={"mock_asr": True})
        assert res2["status"] == JobState.SUCCEEDED.value
        assert res2["media_asset"]["asset_id"] == res1["media_asset"]["asset_id"]


def test_pipeline_cancellation():
    """Cancelling a completed job marks it CANCELLED without corrupting other state."""
    with tempfile.TemporaryDirectory() as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        media_file = tmp_dir / "cancel_input.mp4"
        SyntheticMediaGenerator.generate_valid_mp4(media_file, duration_sec=10)

        orchestrator = PipelineOrchestrator()
        orchestrator.run_pipeline(
            str(media_file), job_id="job_cancel_01", options={"mock_asr": True}
        )

        cancel_res = orchestrator.cancel_pipeline("job_cancel_01")
        assert cancel_res["status"] == JobState.CANCELLED.value

        status_res = orchestrator.get_status("job_cancel_01")
        assert status_res["status"] == JobState.CANCELLED.value
