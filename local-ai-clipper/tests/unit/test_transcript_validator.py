"""
Unit Tests for Transcript Quality Validator.
"""

import pytest
from clipper.core.transcription.validator import TranscriptValidator
from clipper.core.errors import ValidationError
from clipper.domain.models import Transcript, TranscriptSegment, TranscriptWord, ASRProvenance


def test_transcript_validator_valid():
    tx = Transcript(
        transcript_id="tx_12345",
        asset_id="asset_12345",
        duration_seconds=10.0,
        segments=[
            TranscriptSegment(
                segment_id=0,
                start_ms=1000,
                end_ms=3000,
                text="Valid speech segment",
                words=[
                    TranscriptWord(word_id=0, word="Valid", start_ms=1000, end_ms=1500),
                    TranscriptWord(word_id=1, word="speech", start_ms=1510, end_ms=2200),
                    TranscriptWord(word_id=2, word="segment", start_ms=2210, end_ms=3000),
                ],
            )
        ],
        provenance=ASRProvenance(),
    )
    TranscriptValidator.validate_transcript(tx)


def test_transcript_validator_empty_segments_raises():
    tx = Transcript(
        transcript_id="tx_12345",
        asset_id="asset_12345",
        duration_seconds=10.0,
        segments=[],
        provenance=ASRProvenance(),
    )
    with pytest.raises(ValidationError):
        TranscriptValidator.validate_transcript(tx)


def test_transcript_validator_invalid_bounds_raises():
    tx = Transcript(
        transcript_id="tx_12345",
        asset_id="asset_12345",
        duration_seconds=10.0,
        segments=[
            TranscriptSegment(segment_id=0, start_ms=5000, end_ms=3000, text="Bad bounds")
        ],
        provenance=ASRProvenance(),
    )
    with pytest.raises(ValidationError):
        TranscriptValidator.validate_transcript(tx)
