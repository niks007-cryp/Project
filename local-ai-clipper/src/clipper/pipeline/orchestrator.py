"""
Central End-to-End Pipeline Orchestrator for Local AI Clipper.
Coordinates stage execution, checkpointing, resumability, candidate failure isolation, and failure recovery.
"""

import time
from pathlib import Path
from typing import Dict, Any, Optional
from clipper.infrastructure.config import load_config
from clipper.core.manifest import ManifestManager
from clipper.core.state import JobState, JobStateMachine
from clipper.domain.models import JobManifest, StageStatus
from clipper.infrastructure.logger import get_logger
from clipper.pipeline.ingestion_stage import IngestionStage, IngestionStageInput
from clipper.pipeline.transcription_stage import TranscriptionStage, TranscriptionStageInput
from clipper.pipeline.intelligence_stage import IntelligenceStage, IntelligenceStageInput
from clipper.pipeline.reframing_stage import ReframingStage, ReframingStageInput
from clipper.pipeline.rendering_stage import RenderingStage, RenderingStageInput


class PipelineOrchestrator:
    """Central Orchestrator integrating Floors 1-6 into a unified end-to-end pipeline."""

    def __init__(self, logger=None):
        self.config = load_config()
        self.logger = logger or get_logger("orchestrator")

    def run_pipeline(
        self,
        source_file_path: str,
        job_id: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute the full 5-stage pipeline for a given source media file.
        Automatically resumes from the last valid checkpoint on re-invocation.
        """
        options = options or {}
        source_path = Path(source_file_path).resolve()
        jid = job_id or f"job_run_{source_path.stem}"
        job_dir = self.config.jobs_dir / jid
        job_dir.mkdir(parents=True, exist_ok=True)

        manager = ManifestManager(job_dir)
        if (job_dir / "job_manifest.json").exists():
            manifest = manager.load()
        else:
            manifest = JobManifest(job_id=jid)
            manager.save(manifest)

        manifest.status = JobState.RUNNING
        manager.save(manifest)

        start_time = time.time()
        self.logger.info(f"Starting pipeline run for job '{jid}' (Source: {source_path})")

        try:
            # ── Stage 1: Ingestion ──────────────────────────────────────────────
            if not manifest.media_asset:
                self.logger.info("Executing Stage 1: Ingestion")
                ingest_out = IngestionStage(manager, self.logger).run(
                    IngestionStageInput(file_path=str(source_path))
                )
                manifest.media_asset = ingest_out.media_asset
                manifest.stages["ingestion"] = StageStatus(stage_name="ingestion", status="SUCCEEDED")
                manager.save(manifest)
            else:
                self.logger.info("Checkpoint hit: Ingestion already complete.")

            # ── Stage 2: Transcription ──────────────────────────────────────────
            if not manifest.transcript:
                self.logger.info("Executing Stage 2: Transcription")
                tx_out = TranscriptionStage(manager, self.logger).run(
                    TranscriptionStageInput(
                        media_asset=manifest.media_asset,
                        use_mock_provider=options.get("mock_asr", True),
                    )
                )
                manifest.transcript = tx_out.transcript
                manifest.stages["transcription"] = StageStatus(stage_name="transcription", status="SUCCEEDED")
                manager.save(manifest)
            else:
                self.logger.info("Checkpoint hit: Transcription already complete.")

            # ── Stage 3: Content Intelligence ───────────────────────────────────
            if not manifest.candidates:
                self.logger.info("Executing Stage 3: Content Intelligence")
                intel_out = IntelligenceStage(manager, self.logger).run(
                    IntelligenceStageInput(
                        transcript=manifest.transcript,
                        min_duration_sec=options.get("min_duration", 3.0),
                        top_k=options.get("top_k", 3),
                    )
                )
                manifest.candidates = intel_out.selected_candidates
                manifest.stages["intelligence"] = StageStatus(stage_name="intelligence", status="SUCCEEDED")
                manager.save(manifest)
            else:
                self.logger.info("Checkpoint hit: Content Intelligence already complete.")

            # ── Stage 4: Visual Intelligence & Reframing ────────────────────────
            if not manifest.render_plan:
                self.logger.info("Executing Stage 4: Visual Reframing & RenderPlan")
                selected = [c for c in manifest.candidates if c.is_selected] or manifest.candidates
                if not selected:
                    raise ValueError("No valid candidates available for reframing.")
                ref_out = ReframingStage(manager, self.logger).run(
                    ReframingStageInput(
                        candidate=selected[0],
                        media_asset=manifest.media_asset,
                        transcript=manifest.transcript,
                    )
                )
                manifest.render_plan = ref_out.render_plan
                manifest.stages["reframing"] = StageStatus(stage_name="reframing", status="SUCCEEDED")
                manager.save(manifest)
            else:
                self.logger.info("Checkpoint hit: RenderPlan already complete.")

            # ── Stage 5: Video Rendering & Quality Control ──────────────────────
            if not manifest.rendered_asset:
                self.logger.info("Executing Stage 5: Video Rendering & QC")
                rnd_out = RenderingStage(manager, self.logger).run(
                    RenderingStageInput(
                        render_plan=manifest.render_plan,
                        media_asset=manifest.media_asset,
                        profile_id=options.get("profile", "preview"),
                    )
                )
                manifest.rendered_asset = rnd_out.rendered_asset
                manifest.stages["rendering"] = StageStatus(stage_name="rendering", status="SUCCEEDED")
                manifest.status = JobState.SUCCEEDED
                manager.save(manifest)
            else:
                self.logger.info("Checkpoint hit: Video Rendering already complete.")

            # Always mark SUCCEEDED once all stages are confirmed complete
            manifest.status = JobState.SUCCEEDED
            manager.save(manifest)

            duration = round(time.time() - start_time, 2)
            self.logger.info(f"Pipeline completed in {duration}s for job '{jid}'")
            return manifest.model_dump(mode="json")

        except Exception as exc:
            manifest.status = JobState.FAILED
            manifest.stages["pipeline_error"] = StageStatus(
                stage_name="pipeline_error",
                status="FAILED",
                error_message=str(exc),
            )
            manager.save(manifest)
            self.logger.error(f"Pipeline failed for job '{jid}': {exc}")
            raise

    def resume_pipeline(self, job_id: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Resume a previously interrupted pipeline from its last valid checkpoint."""
        job_dir = self.config.jobs_dir / job_id
        manager = ManifestManager(job_dir)
        manifest = manager.load()
        if not manifest.media_asset:
            raise ValueError(f"Job '{job_id}' cannot be resumed: media asset checkpoint missing.")
        self.logger.info(f"Resuming pipeline for job '{job_id}' from status '{manifest.status}'")
        return self.run_pipeline(
            source_file_path=manifest.media_asset.file_path,
            job_id=job_id,
            options=options,
        )

    def cancel_pipeline(self, job_id: str) -> Dict[str, Any]:
        """Cancel a running or queued pipeline job."""
        job_dir = self.config.jobs_dir / job_id
        manager = ManifestManager(job_dir)
        manifest = manager.load()
        manifest.status = JobState.CANCELLED
        manifest.stages["cancellation"] = StageStatus(
            stage_name="cancellation",
            status="CANCELLED",
            error_message="Job cancelled by user request.",
        )
        manager.save(manifest)
        self.logger.info(f"Pipeline job '{job_id}' marked CANCELLED")
        return {"status": JobState.CANCELLED.value, "job_id": job_id}

    def get_status(self, job_id: str) -> Dict[str, Any]:
        """Return the current manifest state for the given job."""
        job_dir = self.config.jobs_dir / job_id
        manager = ManifestManager(job_dir)
        manifest = manager.load()
        return manifest.model_dump(mode="json")
