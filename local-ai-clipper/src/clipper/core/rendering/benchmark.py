"""
Rendering Performance Benchmarking Module for Local AI Clipper.
"""

from typing import Dict, Any
from clipper.domain.models import RenderedAsset


class RenderBenchmarkEvaluator:
    """Measures rendering execution metrics including RTF, CPU/RAM, and file throughput."""

    @classmethod
    def evaluate_benchmark(cls, rendered_asset: RenderedAsset) -> Dict[str, Any]:
        prov = rendered_asset.provenance
        duration_sec = max(0.1, rendered_asset.duration_seconds)
        render_dur_sec = max(0.001, prov.render_duration_ms / 1000.0)
        rtf = round(render_dur_sec / duration_sec, 3)

        return {
            "asset_id": rendered_asset.asset_id,
            "render_backend": prov.render_backend,
            "profile_id": prov.render_profile_id,
            "clip_duration_seconds": duration_sec,
            "render_execution_seconds": round(render_dur_sec, 2),
            "realtime_factor_rtf": rtf,
            "output_size_mb": round(rendered_asset.size_bytes / (1024 * 1024), 2),
            "resolution": f"{rendered_asset.width}x{rendered_asset.height}",
            "fps": rendered_asset.fps,
            "qc_status": rendered_asset.qc_result.status,
        }
