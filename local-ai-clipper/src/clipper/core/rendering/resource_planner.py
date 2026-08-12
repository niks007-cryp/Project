"""
Resource Planner & Storage Governance for Local AI Clipper.
"""

import psutil
from pathlib import Path
from clipper.core.errors import ResourceError
from clipper.domain.models import RenderPlan, RenderProfile


class ResourcePlanner:
    """Estimates disk space requirements and checks host system resource availability."""

    @classmethod
    def check_rendering_resources(
        cls, plan: RenderPlan, profile: RenderProfile, output_dir: Path
    ) -> None:
        duration = max(1.0, plan.duration_seconds)
        bitrate_bps = (profile.bitrate_kbps or 4000) * 1000
        estimated_output_bytes = int((duration * bitrate_bps / 8) * 3.0)  # 3.0x safety factor

        target = Path(output_dir).resolve()
        target.mkdir(parents=True, exist_ok=True)

        try:
            usage = psutil.disk_usage(str(target))
            free_bytes = usage.free
            min_required = estimated_output_bytes + (500 * 1024 * 1024)  # + 500 MB buffer

            if free_bytes < min_required:
                raise ResourceError(
                    f"Insufficient disk space for rendering. Free: {free_bytes / 1e6:.1f}MB, Required: {min_required / 1e6:.1f}MB"
                )
        except Exception as e:
            if isinstance(e, ResourceError):
                raise e
            pass  # Fallback if disk usage check fails
