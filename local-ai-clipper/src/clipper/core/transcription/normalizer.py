"""
Timestamp Normalizer for Transcription Subsystem.
"""

from typing import List, Tuple
from clipper.core.errors import ValidationError
from clipper.domain.models import TranscriptSegment, TranscriptWord


class TimestampNormalizer:
    """Normalizes and aligns word-level and segment-level timestamps."""

    @classmethod
    def normalize_timestamps(
        cls, segments: List[TranscriptSegment], media_duration_seconds: float
    ) -> Tuple[List[TranscriptSegment], int]:
        """
        Normalizes timestamps across segments and words.
        Returns Tuple: (normalized_segments, corrections_count)
        """
        corrections_count = 0
        max_duration_ms = int(round((media_duration_seconds + 0.5) * 1000))

        normalized_segments: List[TranscriptSegment] = []

        for seg_idx, seg in enumerate(segments):
            if seg.start_ms < 0:
                seg.start_ms = 0
                corrections_count += 1

            if seg.start_ms > max_duration_ms:
                raise ValidationError(
                    f"Segment {seg_idx} start timestamp ({seg.start_ms}ms) exceeds media duration ({max_duration_ms}ms)."
                )

            if seg.end_ms <= seg.start_ms:
                raise ValidationError(
                    f"Segment {seg_idx} has invalid duration: start={seg.start_ms}ms, end={seg.end_ms}ms."
                )

            normalized_words: List[TranscriptWord] = []
            words = seg.words

            for w_idx, w in enumerate(words):
                if w.start_ms < 0:
                    w.start_ms = 0
                    corrections_count += 1

                if w.end_ms <= w.start_ms:
                    # Attempt safe delta fix if end <= start by 1ms
                    w.end_ms = w.start_ms + 10
                    corrections_count += 1

                # Safe overlap correction with next word
                if w_idx < len(words) - 1:
                    next_word = words[w_idx + 1]
                    if w.end_ms > next_word.start_ms:
                        overlap_delta = w.end_ms - next_word.start_ms
                        if overlap_delta <= 150:
                            w.end_ms = next_word.start_ms
                            corrections_count += 1
                        else:
                            # Rejects severe overlap
                            raise ValidationError(
                                f"Word overlap delta ({overlap_delta}ms) between '{w.word}' and '{next_word.word}' exceeds safe limit."
                            )

                normalized_words.append(w)

            # Align segment start/end with normalized words
            if normalized_words:
                seg.start_ms = min(seg.start_ms, normalized_words[0].start_ms)
                seg.end_ms = max(seg.end_ms, normalized_words[-1].end_ms)
                seg.words = normalized_words

            normalized_segments.append(seg)

        return normalized_segments, corrections_count
