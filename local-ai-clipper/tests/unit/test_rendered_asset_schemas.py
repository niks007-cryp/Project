"""
Unit Tests for RenderedAsset & RenderJob Domain Schemas.
"""

from clipper.domain.models import (
    RenderedAsset,
    RenderJob,
    QCResult,
    QCStatus,
    RenderProfile,
    RenderingProvenance,
)


def test_rendered_asset_schema_initialization():
    qc = QCResult(status=QCStatus.PASSED, ffprobe_valid=True, av_sync_drift_seconds=0.05)
    prov = RenderingProvenance(
        render_plan_id="plan_001",
        source_asset_id="ast_001",
        source_hash="sha_src",
        render_plan_hash="sha_plan",
        output_hash="sha_out",
        render_backend="CPU",
    )

    asset = RenderedAsset(
        asset_id="rnd_001",
        plan_id="plan_001",
        source_asset_id="ast_001",
        file_path="N:/local-ai-clipper/jobs/job_1/render/outputs/clip_001.mp4",
        filename="clip_001.mp4",
        file_hash_sha256="sha_out",
        size_bytes=1500200,
        duration_seconds=30.0,
        qc_result=qc,
        provenance=prov,
    )

    assert asset.asset_id == "rnd_001"
    assert asset.width == 1080
    assert asset.height == 1920
    assert asset.qc_result.status == QCStatus.PASSED
    assert asset.provenance.render_backend == "CPU"
