"""
Unit Tests for Timestamp Normalizer.
"""

import pytest
from clipper.core.transcription.normalizer import TimestampNormalizer
from clipper.core.errors import ValidationError
from clipper.domain.models import TranscriptSegment, TranscriptWord


def test_timestamp_normalizer_negative_start_clamping():
    seg = TranscriptSegment(
        segment_id=0,
        start_ms=-50,
        end_ms=2000,
        text="Hello world",
        words=[
            TranscriptWord(word_id=0, word="Hello", start_ms=-50, end_ms=1000),
            TranscriptWord(word_id=1, word="world", start_ms=1010, end_ms=2000),
        ],
    )

    norm_segs, corrections = TimestampNormalizer.normalize_timestamps([seg], media_duration_seconds=10.0)
    assert norm_segs[0].start_ms == 0
    assert norm_segs[0].words[0].start_ms == 0
    assert corrections >= 2


def test_timestamp_normalizer_safe_word_overlap_fix():
    seg = TranscriptSegment(
        segment_id=0,
        start_ms=1000,
        end_ms=3000,
        text="Hello world",
        words=[
            TranscriptWord(word_id=0, word="Hello", start_ms=1000, end_ms=2050),
            TranscriptWord(word_id=1, word="world", start_ms=2000, end_ms=3000),
        ],
    )

    norm_segs, corrections = TimestampNormalizer.normalize_timestamps([seg], media_duration_seconds=10.0)
    # Word 0 end_ms should be adjusted to 2000ms (next word's start_ms)
    assert norm_segs[0].words[0].end_ms == 2000
    assert norm_segs[0].words[1].start_ms == 2000


def test_timestamp_normalizer_exceeds_duration_raises():
    seg = TranscriptSegment(
        segment_id=0,
        start_ms=15000,
        end_ms=18000,
        text="Out of bounds",
    )

    with pytest.raises(ValidationError):
        TimestampNormalizer.normalize_timestamps([seg], media_duration_seconds=10.0)
