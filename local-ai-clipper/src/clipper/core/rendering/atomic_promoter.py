"""
Atomic Output Promoter for Local AI Clipper.
Ensures temporary output files (.tmp) are promoted atomically to final target paths (.mp4).
"""

import shutil
from pathlib import Path
from clipper.core.errors import SystemError


class AtomicPromoter:
    """Safely promotes temporary rendered files to final destinations."""

    @classmethod
    def promote_file(cls, temp_path: Path, final_path: Path) -> Path:
        resolved_temp = Path(temp_path).resolve()
        resolved_final = Path(final_path).resolve()

        if not resolved_temp.exists() or resolved_temp.stat().st_size == 0:
            raise SystemError(f"Temporary file '{resolved_temp}' is missing or zero bytes.")

        resolved_final.parent.mkdir(parents=True, exist_ok=True)

        try:
            # Move / overwrite atomically
            shutil.move(str(resolved_temp), str(resolved_final))
            return resolved_final
        except Exception as e:
            raise SystemError(f"Failed to promote temporary file to final path '{resolved_final}': {str(e)}")
