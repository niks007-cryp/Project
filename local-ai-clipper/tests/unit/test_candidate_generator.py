"""
Unit Tests for Candidate Generator.
"""

from clipper.core.intelligence.candidate_generator import CandidateGenerator
from clipper.domain.models import Transcript, TranscriptSegment, ASRProvenance


def test_candidate_generator_duration_bounds():
    # Build 60-second transcript
    segments = [
        TranscriptSegment(segment_id=i, start_ms=i * 5000, end_ms=(i + 1) * 5000, text=f"Sentence number {i + 1}.")
        for i in range(12)
    ]
    tx = Transcript(
        transcript_id="tx_long",
        asset_id="asset_long",
        duration_seconds=60.0,
        segments=segments,
        provenance=ASRProvenance(),
    )

    candidates = CandidateGenerator.generate_candidates(
        tx, min_duration_sec=15.0, max_duration_sec=30.0
    )

    assert len(candidates) > 0
    for cand in candidates:
        assert 15.0 <= cand.duration_seconds <= 30.0
        assert cand.transcript_id == "tx_long"
        assert cand.status == "PROPOSED"
