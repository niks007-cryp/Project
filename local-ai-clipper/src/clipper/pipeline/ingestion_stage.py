"""
Ingestion Pipeline Stage for Local AI Clipper.
"""

from pathlib import Path
from typing import Optional
from pydantic import BaseModel
from clipper.core.manifest import ManifestManager
from clipper.core.ingestion.security_validator import IngestionSecurityValidator
from clipper.core.ingestion.media_validator import MediaValidator
from clipper.core.ingestion.normalizer import MediaNormalizer
from clipper.core.ingestion.hasher import MediaHasher
from clipper.domain.models import MediaAsset, SourceMediaInfo
from clipper.infrastructure.ffmpeg import SafeFFprobe
from clipper.infrastructure.logger import ContextLogger
from clipper.pipeline.stage import BaseStage


class IngestionStageInput(BaseModel):
    file_path: str
    require_audio: bool = False
    force_normalization: bool = False


class IngestionStageOutput(BaseModel):
    media_asset: MediaAsset
    normalized_asset: Optional[MediaAsset] = None
    is_idempotent_skip: bool = False


class IngestionStage(BaseStage[IngestionStageInput, IngestionStageOutput]):
    """
    Production-grade Media Ingestion & Validation Pipeline Stage.
    Flow:
    INPUT -> SECURITY VALIDATION -> FFPROBE -> MEDIA VALIDATION -> NORMALIZATION -> HASHING -> ASSET REGISTRATION -> CHECKPOINT
    """

    stage_name = "ingestion"

    def validate_input(self, input_data: IngestionStageInput) -> None:
        IngestionSecurityValidator.validate_file(Path(input_data.file_path))

    def execute_logic(self, input_data: IngestionStageInput) -> IngestionStageOutput:
        source_path = Path(input_data.file_path).resolve()
        manifest = self.manifest_manager.load()
        job_dir = self.manifest_manager.job_dir

        # 1. Hashing original asset
        file_hash = MediaHasher.calculate_sha256(source_path)
        asset_id = f"asset_{file_hash[:16]}"

        # Idempotency check: if already ingested in manifest, return cached asset
        if manifest.media_asset and manifest.media_asset.file_hash_sha256 == file_hash:
            self.logger.info(f"Idempotent ingestion skip: Asset {asset_id} already registered.")
            return IngestionStageOutput(
                media_asset=manifest.media_asset,
                normalized_asset=manifest.normalized_asset,
                is_idempotent_skip=True,
            )

        # 2. FFprobe analysis
        probe_info = SafeFFprobe.probe_media(source_path)

        # 3. Domain Media Validation
        val_status, has_video, has_audio = MediaValidator.validate_probe_info(
            probe_info, require_audio=input_data.require_audio
        )

        # Construct original MediaAsset
        original_asset = MediaAsset(
            asset_id=asset_id,
            source_id=f"src_{file_hash[:12]}",
            file_path=str(source_path),
            filename=source_path.name,
            extension=source_path.suffix.lower(),
            file_hash_sha256=file_hash,
            size_bytes=probe_info.container.size_bytes,
            duration_seconds=probe_info.container.duration_seconds,
            video_stream=probe_info.video,
            audio_stream=probe_info.audio,
            has_video=has_video,
            has_audio=has_audio,
            is_normalized=False,
            validation_status=val_status,
        )

        # 4. Normalization Evaluation & Execution
        norm_dir = job_dir / "normalized"
        decision, norm_path = MediaNormalizer.normalize_if_needed(
            source_path, norm_dir, probe_info, file_hash
        )

        normalized_asset: Optional[MediaAsset] = None
        if norm_path and norm_path.exists():
            norm_hash = MediaHasher.calculate_sha256(norm_path)
            norm_probe = SafeFFprobe.probe_media(norm_path)
            normalized_asset = MediaAsset(
                asset_id=f"asset_{norm_hash[:16]}",
                source_id=original_asset.source_id,
                parent_asset_id=original_asset.asset_id,
                file_path=str(norm_path),
                filename=norm_path.name,
                extension=".mp4",
                file_hash_sha256=norm_hash,
                size_bytes=norm_probe.container.size_bytes,
                duration_seconds=norm_probe.container.duration_seconds,
                video_stream=norm_probe.video,
                audio_stream=norm_probe.audio,
                has_video=True,
                has_audio=norm_probe.audio is not None,
                is_normalized=True,
                validation_status="SUPPORTED_VALID",
            )

        # Update Manifest
        manifest.media_asset = original_asset
        manifest.normalized_asset = normalized_asset
        if original_asset.video_stream:
            manifest.source_media = SourceMediaInfo(
                file_path=original_asset.file_path,
                file_hash_sha256=original_asset.file_hash_sha256,
                file_size_bytes=original_asset.size_bytes,
                duration_seconds=original_asset.duration_seconds,
                width=original_asset.video_stream.width,
                height=original_asset.video_stream.height,
                fps=original_asset.video_stream.fps,
                video_codec=original_asset.video_stream.codec,
                audio_codec=original_asset.audio_stream.codec if original_asset.audio_stream else "none",
            )
        self.manifest_manager.save(manifest)

        return IngestionStageOutput(
            media_asset=original_asset,
            normalized_asset=normalized_asset,
            is_idempotent_skip=False,
        )

    def validate_output(self, output_data: IngestionStageOutput) -> None:
        if not output_data.media_asset.asset_id:
            raise ValueError("Ingestion output media asset is missing asset_id.")
        if output_data.media_asset.size_bytes <= 0:
            raise ValueError("Ingestion output media asset size is 0 bytes.")
