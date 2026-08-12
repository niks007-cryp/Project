"""
Candidate Deterministic Quality Validator for Content Intelligence Engine.
"""

from typing import Optional
from clipper.core.errors import ValidationError
from clipper.domain.models import ClipCandidate, Transcript, CandidateStatus


class CandidateValidator:
    """Validates structural, temporal, and transcript boundary rules for ClipCandidates."""

    @classmethod
    def validate_candidate(
        cls,
        candidate: ClipCandidate,
        transcript: Optional[Transcript] = None,
        min_duration_sec: float = 15.0,
        max_duration_sec: float = 90.0,
    ) -> None:
        if not candidate.candidate_id:
            raise ValidationError("Candidate is missing candidate_id.")

        if candidate.start_ms < 0:
            raise ValidationError(f"Candidate '{candidate.candidate_id}' contains negative start_ms ({candidate.start_ms}).")

        if candidate.end_ms <= candidate.start_ms:
            raise ValidationError(
                f"Candidate '{candidate.candidate_id}' has invalid bounds: start_ms={candidate.start_ms}, end_ms={candidate.end_ms}."
            )

        duration = (candidate.end_ms - candidate.start_ms) / 1000.0
        effective_min = min_duration_sec
        if transcript and transcript.duration_seconds > 0 and transcript.duration_seconds < min_duration_sec:
            effective_min = max(2.0, transcript.duration_seconds * 0.5)

        if duration < effective_min:
            raise ValidationError(
                f"Candidate '{candidate.candidate_id}' duration ({duration:.2f}s) is below minimum threshold ({effective_min}s)."
            )

        if duration > max_duration_sec:
            raise ValidationError(
                f"Candidate '{candidate.candidate_id}' duration ({duration:.2f}s) exceeds maximum threshold ({max_duration_sec}s)."
            )

        if not candidate.text or not candidate.text.strip():
            raise ValidationError(f"Candidate '{candidate.candidate_id}' contains empty text.")

        if transcript:
            max_duration_ms = int(round((transcript.duration_seconds + 0.5) * 1000))
            if candidate.end_ms > max_duration_ms:
                raise ValidationError(
                    f"Candidate '{candidate.candidate_id}' end_ms ({candidate.end_ms}ms) exceeds transcript duration ({max_duration_ms}ms)."
                )

        candidate.status = CandidateStatus.VALIDATED
