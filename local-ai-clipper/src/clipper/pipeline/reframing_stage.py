"""
Reframing & RenderPlan Pipeline Stage for Local AI Clipper.
"""

import hashlib
import json
from pathlib import Path
from typing import Optional, List
from pydantic import BaseModel, Field
from clipper.core.errors import InputError, ValidationError
from clipper.core.manifest import ManifestManager
from clipper.core.vision.analyzer import VisualAnalyzer
from clipper.core.vision.tracker import SubjectTracker
from clipper.core.vision.crop_planner import CropPlanner
from clipper.core.captions.segmenter import CaptionSegmenter
from clipper.core.captions.styler import CaptionStyler
from clipper.core.vision.collision_engine import CollisionAvoidanceEngine
from clipper.core.vision.renderplan_validator import RenderPlanValidator
from clipper.domain.models import (
    ClipCandidate,
    MediaAsset,
    Transcript,
    RenderPlan,
    RenderPlanProvenance,
)
from clipper.pipeline.stage import BaseStage


class ReframingStageInput(BaseModel):
    candidate: ClipCandidate
    media_asset: MediaAsset
    transcript: Transcript
    target_width: int = 1080
    target_height: int = 1920


class ReframingStageOutput(BaseModel):
    render_plan: RenderPlan
    is_idempotent_skip: bool = False


class ReframingStage(BaseStage[ReframingStageInput, ReframingStageOutput]):
    """
    Production-grade Visual Intelligence, Auto-Reframing & Captions Stage.
    Outputs validated RenderPlan JSON artifact.
    """

    stage_name = "reframing"

    def validate_input(self, input_data: ReframingStageInput) -> None:
        if not input_data.candidate:
            raise InputError("Input candidate is missing.")
        if not input_data.media_asset:
            raise InputError("Input media_asset is missing.")
        if not input_data.transcript:
            raise InputError("Input transcript is missing.")

    def execute_logic(self, input_data: ReframingStageInput) -> ReframingStageOutput:
        cand = input_data.candidate
        asset = input_data.media_asset
        tx = input_data.transcript
        manifest = self.manifest_manager.load()
        job_dir = self.manifest_manager.job_dir

        # Hash for idempotency check
        config_payload = json.dumps(
            {
                "candidate_id": cand.candidate_id,
                "target_w": input_data.target_width,
                "target_h": input_data.target_height,
            },
            sort_keys=True,
        )
        config_hash = hashlib.sha256(config_payload.encode("utf-8")).hexdigest()[:12]

        if manifest.render_plan and manifest.metadata.get("reframing_config_hash") == config_hash:
            self.logger.info(f"Idempotent reframing skip: RenderPlan for candidate {cand.candidate_id} already generated.")
            return ReframingStageOutput(render_plan=manifest.render_plan, is_idempotent_skip=True)

        # 1. Visual Analysis
        self.logger.info(f"Analyzing visual subject motion for asset {asset.asset_id}...")
        subject_boxes = VisualAnalyzer.analyze_asset(asset, sample_interval_ms=500)

        # 2. Subject Tracking & Trajectory Generation
        raw_kfs = SubjectTracker.generate_trajectory(
            subject_boxes, start_ms=cand.start_ms, end_ms=cand.end_ms
        )

        # 3. Crop Planning & Safe Zone Constraint
        constrained_kfs = CropPlanner.validate_and_constrain_keyframes(raw_kfs)

        # 4. Caption Segmentation & Styling
        raw_captions = CaptionSegmenter.segment_candidate_captions(cand, tx)
        caption_style = CaptionStyler.get_default_style()

        # 5. Collision Avoidance Engine
        resolved_captions, collisions_count = CollisionAvoidanceEngine.resolve_collisions(
            raw_captions, subject_boxes
        )

        # 6. RenderPlan Assembly
        prov = RenderPlanProvenance(
            candidate_id=cand.candidate_id,
            transcript_id=tx.transcript_id,
            reframing_version="v1.0.0",
            caption_version="v1.0.0",
            collision_version="v1.0.0",
            config_hash=config_hash,
        )

        plan = RenderPlan(
            plan_id=f"plan_{cand.candidate_id}",
            candidate_id=cand.candidate_id,
            source_asset_id=asset.asset_id,
            start_ms=cand.start_ms,
            end_ms=cand.end_ms,
            duration_seconds=cand.duration_seconds,
            target_width=input_data.target_width,
            target_height=input_data.target_height,
            crop_keyframes=constrained_kfs,
            caption_segments=resolved_captions,
            caption_style=caption_style,
            collisions_resolved=collisions_count,
            provenance=prov,
        )

        # 7. RenderPlan Validation
        RenderPlanValidator.validate_plan(plan)

        # Save RenderPlan JSON artifact to job directory
        plan_file = job_dir / "renderplan.json"
        with open(plan_file, "w", encoding="utf-8") as f:
            json.dump(plan.model_dump(mode="json"), f, indent=2, default=str)

        manifest.render_plan = plan
        manifest.metadata["reframing_config_hash"] = config_hash
        self.manifest_manager.save(manifest)

        return ReframingStageOutput(render_plan=plan, is_idempotent_skip=False)

    def validate_output(self, output_data: ReframingStageOutput) -> None:
        RenderPlanValidator.validate_plan(output_data.render_plan)
