"""
Caption Segmenter & Line Breaker for Local AI Clipper.
Formated subtitle chunks from Transcript words with reading-speed validation.
"""

from typing import List
from clipper.domain.models import (
    Transcript,
    CaptionSegment,
    CaptionWord,
    ClipCandidate,
)


class CaptionSegmenter:
    """Segments transcript word timestamps into readable subtitle blocks."""

    @classmethod
    def segment_candidate_captions(
        cls,
        candidate: ClipCandidate,
        transcript: Transcript,
        max_chars_per_line: int = 35,
        max_lines: int = 2,
        max_cps: float = 25.0,
    ) -> List[CaptionSegment]:
        caption_segments: List[CaptionSegment] = []

        # Find words falling within candidate timestamp bounds
        target_words: List[CaptionWord] = []
        for seg in transcript.segments:
            for w in seg.words:
                if candidate.start_ms <= w.start_ms and w.end_ms <= candidate.end_ms:
                    target_words.append(
                        CaptionWord(
                            word=w.word,
                            start_ms=w.start_ms,
                            end_ms=w.end_ms,
                        )
                    )

        if not target_words:
            # Fallback segment from candidate text
            caption_segments.append(
                CaptionSegment(
                    segment_id=0,
                    start_ms=candidate.start_ms,
                    end_ms=candidate.end_ms,
                    text=candidate.text[:70],
                    lines=[candidate.text[:35], candidate.text[35:70]],
                    position_vertical="bottom",
                )
            )
            return caption_segments

        # Group words into chunks of max 8 words or 70 characters
        chunk_size = 7
        seg_counter = 0
        for i in range(0, len(target_words), chunk_size):
            chunk = target_words[i : i + chunk_size]
            start_ts = chunk[0].start_ms
            end_ts = chunk[-1].end_ms
            combined_text = " ".join(w.word for w in chunk)

            # Line breaking logic
            words_in_text = combined_text.split()
            line1, line2 = "", ""
            for word in words_in_text:
                if len(line1) + len(word) + 1 <= max_chars_per_line:
                    line1 = f"{line1} {word}".strip()
                elif len(line2) + len(word) + 1 <= max_chars_per_line:
                    line2 = f"{line2} {word}".strip()

            lines = [line for line in [line1, line2] if line]
            if not lines:
                lines = [combined_text[:max_chars_per_line]]

            caption_segments.append(
                CaptionSegment(
                    segment_id=seg_counter,
                    start_ms=start_ts,
                    end_ms=end_ts,
                    text=combined_text,
                    lines=lines,
                    words=chunk,
                    position_vertical="bottom",
                    vertical_margin_pct=10.0,
                )
            )
            seg_counter += 1

        return caption_segments
