"""
Integration Tests for Media Ingestion Pipeline Stage across Formats.
"""

import pytest
from pathlib import Path
from clipper.pipeline.ingestion_stage import IngestionStage, IngestionStageInput
from clipper.core.errors import CorruptMediaError, UnsupportedMediaFormatError
from tests.fixtures.media_generator import SyntheticMediaGenerator


def test_ingestion_mp4(manifest_manager, logger, temp_job_dir):
    mp4_path = temp_job_dir / "sample.mp4"
    SyntheticMediaGenerator.generate_valid_mp4(mp4_path)

    stage = IngestionStage(manifest_manager, logger)
    inp = IngestionStageInput(file_path=str(mp4_path))

    out = stage.run(inp)
    assert out.media_asset.asset_id.startswith("asset_")
    assert out.media_asset.filename == "sample.mp4"
    assert out.media_asset.duration_seconds > 0.0
    assert out.media_asset.has_video is True
    assert out.media_asset.has_audio is True
    assert out.is_idempotent_skip is False

    # Assert saved to manifest
    manifest = manifest_manager.load()
    assert manifest.media_asset is not None
    assert manifest.media_asset.asset_id == out.media_asset.asset_id
    assert manifest.stages["ingestion"].status == "SUCCEEDED"


def test_ingestion_m4v(manifest_manager, logger, temp_job_dir):
    m4v_path = temp_job_dir / "sample.m4v"
    SyntheticMediaGenerator.generate_valid_m4v(m4v_path)

    stage = IngestionStage(manifest_manager, logger)
    inp = IngestionStageInput(file_path=str(m4v_path))

    out = stage.run(inp)
    assert out.media_asset.extension == ".m4v"
    assert out.media_asset.duration_seconds > 0.0
    assert out.media_asset.has_video is True
    assert out.media_asset.has_audio is True


def test_ingestion_idempotency(manifest_manager, logger, temp_job_dir):
    mp4_path = temp_job_dir / "sample_idempotent.mp4"
    SyntheticMediaGenerator.generate_valid_mp4(mp4_path)

    stage = IngestionStage(manifest_manager, logger)
    inp = IngestionStageInput(file_path=str(mp4_path))

    # First run
    out1 = stage.run(inp)
    assert out1.is_idempotent_skip is False

    # Second run on same manifest
    out2 = stage.run(inp)
    assert out2.is_idempotent_skip is True
    assert out2.media_asset.asset_id == out1.media_asset.asset_id


def test_ingestion_mov(manifest_manager, logger, temp_job_dir):
    mov_path = temp_job_dir / "sample.mov"
    SyntheticMediaGenerator.generate_valid_mov(mov_path)

    stage = IngestionStage(manifest_manager, logger)
    out = stage.run(IngestionStageInput(file_path=str(mov_path)))
    assert out.media_asset.extension == ".mov"


def test_ingestion_mkv(manifest_manager, logger, temp_job_dir):
    mkv_path = temp_job_dir / "sample.mkv"
    SyntheticMediaGenerator.generate_valid_mkv(mkv_path)

    stage = IngestionStage(manifest_manager, logger)
    out = stage.run(IngestionStageInput(file_path=str(mkv_path)))
    assert out.media_asset.extension == ".mkv"


def test_ingestion_webm(manifest_manager, logger, temp_job_dir):
    webm_path = temp_job_dir / "sample.webm"
    SyntheticMediaGenerator.generate_valid_webm(webm_path)

    stage = IngestionStage(manifest_manager, logger)
    out = stage.run(IngestionStageInput(file_path=str(webm_path)))
    assert out.media_asset.extension == ".webm"


def test_ingestion_video_only(manifest_manager, logger, temp_job_dir):
    vo_path = temp_job_dir / "video_only.mp4"
    SyntheticMediaGenerator.generate_video_only(vo_path)

    stage = IngestionStage(manifest_manager, logger)
    out = stage.run(IngestionStageInput(file_path=str(vo_path), require_audio=False))
    assert out.media_asset.has_video is True
    assert out.media_asset.has_audio is False


def test_ingestion_corrupt_media_raises(manifest_manager, logger, temp_job_dir):
    corrupt_path = temp_job_dir / "corrupt.mp4"
    SyntheticMediaGenerator.generate_corrupt_file(corrupt_path)

    stage = IngestionStage(manifest_manager, logger)
    with pytest.raises((CorruptMediaError, Exception)):
        stage.run(IngestionStageInput(file_path=str(corrupt_path)))


def test_ingestion_rotated_video_normalizes(manifest_manager, logger, temp_job_dir):
    rot_path = temp_job_dir / "rotated.mp4"
    SyntheticMediaGenerator.generate_rotated_video(rot_path)

    stage = IngestionStage(manifest_manager, logger)
    out = stage.run(IngestionStageInput(file_path=str(rot_path)))
    
    assert out.normalized_asset is not None
    assert out.normalized_asset.is_normalized is True
    assert Path(out.normalized_asset.file_path).exists()
