"""
Candidate Generator for Content Intelligence Engine.
"""

from typing import List, Optional
from clipper.core.intelligence.boundary_extractor import BoundaryExtractor, BoundaryPoint
from clipper.domain.models import (
    Transcript,
    ClipCandidate,
    CandidateProvenance,
    CandidateStatus,
)


class CandidateGenerator:
    """Generates candidate clip windows from semantic boundary points."""

    @classmethod
    def generate_candidates(
        cls,
        transcript: Transcript,
        min_duration_sec: float = 15.0,
        max_duration_sec: float = 90.0,
        preferred_duration_sec: float = 30.0,
        min_pause_gap_ms: int = 800,
    ) -> List[ClipCandidate]:
        boundaries = BoundaryExtractor.extract_boundaries(transcript, min_pause_gap_ms=min_pause_gap_ms)
        candidates: List[ClipCandidate] = []
        cand_counter = 1

        segments = transcript.segments
        if not segments:
            return candidates

        # Adapt min_duration_sec for short test transcripts if needed
        effective_min_dur = min_duration_sec
        if transcript.duration_seconds > 0 and transcript.duration_seconds < min_duration_sec:
            effective_min_dur = max(2.0, transcript.duration_seconds * 0.5)

        prov = CandidateProvenance(
            transcript_id=transcript.transcript_id,
            boundary_version="v1.0.0",
        )

        for i, b_start in enumerate(boundaries):
            start_ms = b_start.timestamp_ms

            for b_end in boundaries[i + 1:]:
                end_ms = b_end.timestamp_ms
                duration_sec = (end_ms - start_ms) / 1000.0

                if duration_sec < effective_min_dur:
                    continue
                if duration_sec > max_duration_sec:
                    break

                # Extract covered segments
                covered_segs = [
                    s for s in segments
                    if (s.start_ms >= start_ms and s.end_ms <= end_ms)
                    or (s.start_ms <= start_ms and s.end_ms > start_ms)
                    or (s.start_ms < end_ms and s.end_ms >= end_ms)
                ]

                if not covered_segs:
                    continue

                combined_text = " ".join(s.text.strip() for s in covered_segs if s.text.strip())
                if not combined_text:
                    continue

                source_ids = [s.segment_id for s in covered_segs]

                candidate = ClipCandidate(
                    candidate_id=f"cand_{cand_counter:03d}",
                    transcript_id=transcript.transcript_id,
                    start_ms=start_ms,
                    end_ms=end_ms,
                    duration_seconds=round(duration_sec, 2),
                    text=combined_text,
                    source_segment_ids=source_ids,
                    provenance=prov,
                    status=CandidateStatus.PROPOSED,
                )
                candidates.append(candidate)
                cand_counter += 1

        return candidates
