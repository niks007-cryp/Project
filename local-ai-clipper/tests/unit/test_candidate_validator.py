"""
Unit Tests for Candidate Validator.
"""

import pytest
from clipper.core.intelligence.validator import CandidateValidator
from clipper.core.errors import ValidationError
from clipper.domain.models import ClipCandidate, CandidateProvenance, Transcript, TranscriptSegment, ASRProvenance


def test_candidate_validator_valid():
    prov = CandidateProvenance(transcript_id="tx_123")
    candidate = ClipCandidate(
        candidate_id="cand_001",
        transcript_id="tx_123",
        start_ms=1000,
        end_ms=31000,
        duration_seconds=30.0,
        text="Valid transcript clip candidate text.",
        provenance=prov,
    )
    tx = Transcript(
        transcript_id="tx_123",
        asset_id="asset_123",
        duration_seconds=60.0,
        segments=[TranscriptSegment(segment_id=0, start_ms=0, end_ms=60000, text="Full text")],
        provenance=ASRProvenance(),
    )
    CandidateValidator.validate_candidate(candidate, transcript=tx)
    assert candidate.status == "VALIDATED"


def test_candidate_validator_too_short_raises():
    prov = CandidateProvenance(transcript_id="tx_123")
    candidate = ClipCandidate(
        candidate_id="cand_short",
        transcript_id="tx_123",
        start_ms=1000,
        end_ms=5000,  # 4 seconds
        duration_seconds=4.0,
        text="Short clip.",
        provenance=prov,
    )
    with pytest.raises(ValidationError):
        CandidateValidator.validate_candidate(candidate, min_duration_sec=15.0)


def test_candidate_validator_exceeds_transcript_raises():
    prov = CandidateProvenance(transcript_id="tx_123")
    candidate = ClipCandidate(
        candidate_id="cand_oob",
        transcript_id="tx_123",
        start_ms=1000,
        end_ms=75000,  # 75s
        duration_seconds=74.0,
        text="Out of bounds clip.",
        provenance=prov,
    )
    tx = Transcript(
        transcript_id="tx_123",
        asset_id="asset_123",
        duration_seconds=60.0,  # 60s max
        segments=[TranscriptSegment(segment_id=0, start_ms=0, end_ms=60000, text="Full text")],
        provenance=ASRProvenance(),
    )
    with pytest.raises(ValidationError):
        CandidateValidator.validate_candidate(candidate, transcript=tx, max_duration_sec=90.0)


def test_candidate_validator_empty_text_raises():
    prov = CandidateProvenance(transcript_id="tx_123")
    candidate = ClipCandidate(
        candidate_id="cand_empty",
        transcript_id="tx_123",
        start_ms=1000,
        end_ms=25000,
        duration_seconds=24.0,
        text="",
        provenance=prov,
    )
    with pytest.raises(ValidationError):
        CandidateValidator.validate_candidate(candidate)
