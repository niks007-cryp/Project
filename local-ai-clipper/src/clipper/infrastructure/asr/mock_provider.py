"""
Mock ASR Provider for Testing Local AI Clipper.
"""

from pathlib import Path
from clipper.domain.models import TranscriptSegment, TranscriptWord
from clipper.infrastructure.asr.base_provider import ASRProvider, ASRConfig, RawASRResult


class MockASRProvider(ASRProvider):
    """Synthetic ASR Provider for fast unit and integration testing."""

    def transcribe(self, audio_path: Path, config: ASRConfig) -> RawASRResult:
        segments = [
            TranscriptSegment(
                segment_id=0,
                speaker_id="SPEAKER_00",
                start_ms=1000,
                end_ms=4000,
                text="Welcome to the local AI video clipping platform.",
                avg_confidence=0.98,
                words=[
                    TranscriptWord(word_id=0, word="Welcome", start_ms=1000, end_ms=1500, confidence=0.99),
                    TranscriptWord(word_id=1, word="to", start_ms=1510, end_ms=1700, confidence=0.98),
                    TranscriptWord(word_id=2, word="the", start_ms=1710, end_ms=1900, confidence=0.99),
                    TranscriptWord(word_id=3, word="local", start_ms=1910, end_ms=2300, confidence=0.97),
                    TranscriptWord(word_id=4, word="AI", start_ms=2310, end_ms=2700, confidence=0.99),
                    TranscriptWord(word_id=5, word="video", start_ms=2710, end_ms=3100, confidence=0.98),
                    TranscriptWord(word_id=6, word="clipping", start_ms=3110, end_ms=3500, confidence=0.96),
                    TranscriptWord(word_id=7, word="platform.", start_ms=3510, end_ms=4000, confidence=0.98),
                ],
            ),
            TranscriptSegment(
                segment_id=1,
                speaker_id="SPEAKER_00",
                start_ms=4500,
                end_ms=7500,
                text="It automatically identifies viral short form content.",
                avg_confidence=0.96,
                words=[
                    TranscriptWord(word_id=0, word="It", start_ms=4500, end_ms=4700, confidence=0.99),
                    TranscriptWord(word_id=1, word="automatically", start_ms=4710, end_ms=5300, confidence=0.95),
                    TranscriptWord(word_id=2, word="identifies", start_ms=5310, end_ms=5900, confidence=0.96),
                    TranscriptWord(word_id=3, word="viral", start_ms=5910, end_ms=6300, confidence=0.97),
                    TranscriptWord(word_id=4, word="short", start_ms=6310, end_ms=6700, confidence=0.98),
                    TranscriptWord(word_id=5, word="form", start_ms=6710, end_ms=7000, confidence=0.96),
                    TranscriptWord(word_id=6, word="content.", start_ms=7010, end_ms=7500, confidence=0.98),
                ],
            ),
        ]

        return RawASRResult(
            segments=segments,
            language_detected="en",
            language_probability=0.99,
            device_used=config.device if config.device != "auto" else "cpu",
            compute_type_used=config.compute_type if config.compute_type != "auto" else "int8",
            execution_duration_ms=150.0,
        )
