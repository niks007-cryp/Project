"""
Transcript Quality Validator for Transcription Subsystem.
"""

from clipper.core.errors import ValidationError
from clipper.domain.models import Transcript


class TranscriptValidator:
    """Validates structural, temporal, and metadata assertions on Transcript entities."""

    @classmethod
    def validate_transcript(cls, transcript: Transcript) -> None:
        if not transcript.transcript_id:
            raise ValidationError("Transcript is missing transcript_id.")

        if not transcript.asset_id:
            raise ValidationError("Transcript is missing asset_id.")

        if transcript.duration_seconds <= 0.0:
            raise ValidationError(f"Invalid transcript duration: {transcript.duration_seconds}")

        if not transcript.segments:
            raise ValidationError("Transcript contains no segments.")

        prev_end_ms = 0
        for seg in transcript.segments:
            if seg.start_ms < 0:
                raise ValidationError(f"Segment {seg.segment_id} contains negative start timestamp.")
            if seg.end_ms <= seg.start_ms:
                raise ValidationError(f"Segment {seg.segment_id} has invalid start/end bounds.")
            if not seg.text or not seg.text.strip():
                raise ValidationError(f"Segment {seg.segment_id} contains empty text.")

            if seg.words:
                prev_word_end = seg.start_ms
                for w in seg.words:
                    if w.start_ms < prev_word_end:
                        # Allow slight overlap up to 5ms
                        if (prev_word_end - w.start_ms) > 5:
                            raise ValidationError(
                                f"Word '{w.word}' timestamp ({w.start_ms}ms) is non-monotonic relative to previous end ({prev_word_end}ms)."
                            )
                    prev_word_end = w.end_ms

            prev_end_ms = seg.end_ms
