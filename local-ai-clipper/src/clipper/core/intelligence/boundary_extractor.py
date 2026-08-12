"""
Semantic Boundary Extractor for Content Intelligence Engine.
"""

from typing import List
from pydantic import BaseModel
from clipper.domain.models import Transcript, TranscriptSegment


class BoundaryPoint(BaseModel):
    timestamp_ms: int
    segment_idx: int
    boundary_type: str  # SENTENCE_END, PAUSE_GAP, SPEAKER_TURN, TOPIC_SHIFT, START, END
    confidence: float = 1.0


class BoundaryExtractor:
    """Extracts semantic boundary timestamps from Transcript segments."""

    @classmethod
    def extract_boundaries(cls, transcript: Transcript, min_pause_gap_ms: int = 800) -> List[BoundaryPoint]:
        boundaries: List[BoundaryPoint] = []
        segments = transcript.segments

        if not segments:
            return boundaries

        # Add initial start boundary
        boundaries.append(BoundaryPoint(timestamp_ms=segments[0].start_ms, segment_idx=0, boundary_type="START"))

        for idx, seg in enumerate(segments):
            text = seg.text.strip()
            b_type = "SENTENCE_END" if (text and text[-1] in [".", "!", "?"]) else "SEGMENT_END"

            # Check for pause gap with next segment
            if idx < len(segments) - 1:
                next_seg = segments[idx + 1]
                gap_ms = next_seg.start_ms - seg.end_ms
                if gap_ms >= min_pause_gap_ms:
                    b_type = "PAUSE_GAP"

                if seg.speaker_id and next_seg.speaker_id and seg.speaker_id != next_seg.speaker_id:
                    b_type = "SPEAKER_TURN"

            boundaries.append(BoundaryPoint(timestamp_ms=seg.end_ms, segment_idx=idx, boundary_type=b_type))

        # Add final end boundary if missing
        if not boundaries or boundaries[-1].timestamp_ms != segments[-1].end_ms:
            boundaries.append(
                BoundaryPoint(timestamp_ms=segments[-1].end_ms, segment_idx=len(segments) - 1, boundary_type="END")
            )

        # Deduplicate and sort by timestamp_ms
        unique_boundaries: List[BoundaryPoint] = []
        seen_ts = set()
        for b in sorted(boundaries, key=lambda x: x.timestamp_ms):
            if b.timestamp_ms not in seen_ts:
                unique_boundaries.append(b)
                seen_ts.add(b.timestamp_ms)

        return unique_boundaries
