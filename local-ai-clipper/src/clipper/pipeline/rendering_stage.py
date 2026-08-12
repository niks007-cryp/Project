"""
Video Rendering Pipeline Stage for Local AI Clipper.
Converts validated RenderPlan into production RenderedAsset with QC verification.
"""

import hashlib
import json
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field
from clipper.core.errors import InputError, ValidationError, SystemError
from clipper.core.manifest import ManifestManager, calculate_file_hash
from clipper.core.rendering.plan_validator import RenderPlanPreValidator
from clipper.core.rendering.profiles import RenderProfileRegistry
from clipper.core.rendering.resource_planner import ResourcePlanner
from clipper.core.rendering.engine import RenderEngine
from clipper.core.rendering.qc_engine import QualityControlEngine
from clipper.core.rendering.atomic_promoter import AtomicPromoter
from clipper.domain.models import (
    RenderPlan,
    MediaAsset,
    RenderedAsset,
    RenderingProvenance,
    RenderProfile,
    QCStatus,
)
from clipper.pipeline.stage import BaseStage


class RenderingStageInput(BaseModel):
    render_plan: RenderPlan
    media_asset: MediaAsset
    profile_id: str = "short_1080"
    preferred_backend: str = "auto"


class RenderingStageOutput(BaseModel):
    rendered_asset: RenderedAsset
    is_idempotent_skip: bool = False


class RenderingStage(BaseStage[RenderingStageInput, RenderingStageOutput]):
    """
    Production-grade Video Rendering & Quality Control Pipeline Stage.
    Produces validated RenderedAsset MP4 artifact.
    """

    stage_name = "rendering"

    def validate_input(self, input_data: RenderingStageInput) -> None:
        if not input_data.render_plan:
            raise InputError("Input render_plan is missing.")
        if not input_data.media_asset:
            raise InputError("Input media_asset is missing.")

    def execute_logic(self, input_data: RenderingStageInput) -> RenderingStageOutput:
        plan = input_data.render_plan
        asset = input_data.media_asset
        manifest = self.manifest_manager.load()
        job_dir = self.manifest_manager.job_dir

        profile = RenderProfileRegistry.get_profile(input_data.profile_id)

        # Pre-render validation
        RenderPlanPreValidator.validate_for_rendering(plan, asset)

        # Idempotency Hash Check
        config_payload = json.dumps(
            {
                "plan_id": plan.plan_id,
                "profile": profile.profile_id,
                "asset_hash": asset.file_hash_sha256,
            },
            sort_keys=True,
        )
        config_hash = hashlib.sha256(config_payload.encode("utf-8")).hexdigest()[:12]

        if manifest.rendered_asset and manifest.metadata.get("rendering_config_hash") == config_hash:
            final_path = Path(manifest.rendered_asset.file_path)
            if final_path.exists() and final_path.stat().st_size > 0:
                self.logger.info(f"Idempotent rendering skip: RenderedAsset for plan {plan.plan_id} already exists.")
                return RenderingStageOutput(rendered_asset=manifest.rendered_asset, is_idempotent_skip=True)

        # Directories
        render_dir = job_dir / "render"
        temp_dir = render_dir / "temporary"
        output_dir = render_dir / "outputs"
        temp_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Resource Governance
        ResourcePlanner.check_rendering_resources(plan, profile, output_dir)

        # Temporary files
        temp_output_path = temp_dir / f"clip_{plan.candidate_id}.tmp"
        temp_ass_path = temp_dir / f"subtitles_{plan.candidate_id}.ass"
        final_mp4_path = output_dir / f"clip_{plan.candidate_id}.mp4"

        # Execute Video Rendering Engine
        self.logger.info(f"Executing video rendering engine for plan '{plan.plan_id}' (Profile: {profile.profile_id})...")
        rendered_tmp, backend_used, fallback_reason, render_duration_ms = RenderEngine.render_clip(
            plan=plan,
            media_asset=asset,
            profile=profile,
            temp_output_path=temp_output_path,
            temp_ass_path=temp_ass_path,
            preferred_backend=input_data.preferred_backend,
        )

        # Post-Render Quality Control Evaluation
        qc_result = QualityControlEngine.evaluate_output(rendered_tmp, profile)
        if qc_result.status == QCStatus.FAILED:
            raise SystemError(f"Rendered asset failed quality control: {', '.join(qc_result.errors)}")

        # Atomic Promotion (.tmp -> .mp4)
        final_output = AtomicPromoter.promote_file(rendered_tmp, final_mp4_path)

        # Hashing & Provenance
        out_hash = calculate_file_hash(final_output)
        source_hash = asset.file_hash_sha256
        plan_hash = hashlib.sha256(plan.model_dump_json().encode("utf-8")).hexdigest()

        rtf = round((plan.duration_seconds / (render_duration_ms / 1000.0)), 2) if render_duration_ms > 0 else 0.0

        prov = RenderingProvenance(
            render_plan_id=plan.plan_id,
            source_asset_id=asset.asset_id,
            source_hash=source_hash,
            render_plan_hash=plan_hash,
            output_hash=out_hash,
            render_backend=backend_used,
            fallback_reason=fallback_reason,
            render_profile_id=profile.profile_id,
            ffmpeg_version="ffmpeg-master",
            render_duration_ms=render_duration_ms,
            realtime_factor=rtf,
        )

        rendered_asset = RenderedAsset(
            asset_id=f"rnd_{plan.candidate_id}",
            plan_id=plan.plan_id,
            source_asset_id=asset.asset_id,
            file_path=str(final_output),
            filename=final_output.name,
            file_hash_sha256=out_hash,
            size_bytes=final_output.stat().st_size,
            duration_seconds=plan.duration_seconds,
            width=profile.target_width,
            height=profile.target_height,
            fps=profile.fps,
            video_codec=profile.video_codec,
            audio_codec=profile.audio_codec,
            pixel_format=profile.pixel_format,
            qc_result=qc_result,
            provenance=prov,
        )

        # Save RenderedAsset metadata to job directory
        asset_file = render_dir / "rendered_asset.json"
        with open(asset_file, "w", encoding="utf-8") as f:
            json.dump(rendered_asset.model_dump(mode="json"), f, indent=2, default=str)

        manifest.rendered_asset = rendered_asset
        manifest.metadata["rendering_config_hash"] = config_hash
        self.manifest_manager.save(manifest)

        return RenderingStageOutput(rendered_asset=rendered_asset, is_idempotent_skip=False)

    def validate_output(self, output_data: RenderingStageOutput) -> None:
        if not output_data.rendered_asset:
            raise ValueError("RenderingStageOutput is missing rendered_asset.")
        if output_data.rendered_asset.qc_result.status == QCStatus.FAILED:
            raise ValueError("RenderingStageOutput rendered_asset failed QC.")
