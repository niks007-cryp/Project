"""
Unit Tests for Boundary Extractor.
"""

from clipper.core.intelligence.boundary_extractor import BoundaryExtractor
from clipper.domain.models import Transcript, TranscriptSegment, ASRProvenance


def test_boundary_extractor_sentence_and_pause_gaps():
    tx = Transcript(
        transcript_id="tx_test",
        asset_id="asset_test",
        duration_seconds=30.0,
        segments=[
            TranscriptSegment(segment_id=0, start_ms=0, end_ms=3000, text="First sentence."),
            TranscriptSegment(segment_id=1, start_ms=4500, end_ms=8000, text="Second sentence!"),  # 1500ms gap
            TranscriptSegment(segment_id=2, start_ms=8100, end_ms=12000, text="Third sentence?"),
        ],
        provenance=ASRProvenance(),
    )

    boundaries = BoundaryExtractor.extract_boundaries(tx, min_pause_gap_ms=800)
    assert len(boundaries) >= 3
    types = [b.boundary_type for b in boundaries]
    assert "SENTENCE_END" in types
    assert "PAUSE_GAP" in types
