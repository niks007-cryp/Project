"""
FasterWhisper Concrete ASR Provider for Local AI Clipper.
"""

import time
from pathlib import Path
from typing import Optional, List, Tuple
from clipper.core.errors import ModelError, SystemError
from clipper.domain.models import TranscriptSegment, TranscriptWord
from clipper.infrastructure.asr.base_provider import ASRProvider, ASRConfig, RawASRResult

MODEL_NAME_MAP = {
    "whisper-tiny": "tiny",
    "whisper-base": "base",
    "whisper-small": "small",
    "whisper-medium": "medium",
    "whisper-large-v3": "large-v3",
}


class FasterWhisperProvider(ASRProvider):
    """Concrete ASR Provider using faster-whisper (CTranslate2)."""

    def transcribe(self, audio_path: Path, config: ASRConfig) -> RawASRResult:
        import torch
        from faster_whisper import WhisperModel

        resolved_audio = Path(audio_path).resolve()
        if not resolved_audio.exists():
            raise ModelError(f"Audio file for transcription does not exist: {resolved_audio}")

        # Map whisper-tiny -> tiny etc.
        model_size = MODEL_NAME_MAP.get(config.model_name.lower(), config.model_name)

        # Determine execution hardware (CUDA vs CPU fallback)
        target_device = config.device
        if target_device == "auto":
            target_device = "cuda" if torch.cuda.is_available() else "cpu"

        target_compute = config.compute_type
        if target_compute == "auto":
            target_compute = "float16" if target_device == "cuda" else "int8"

        t0 = time.time()
        model: Optional[WhisperModel] = None

        # Attempt primary hardware loading, with CPU fallback if CUDA fails
        try:
            model = WhisperModel(
                model_size,
                device=target_device,
                compute_type=target_compute,
            )
        except Exception as e:
            if target_device == "cuda":
                # CUDA Fallback to CPU
                target_device = "cpu"
                target_compute = "int8"
                try:
                    model = WhisperModel(
                        model_size,
                        device=target_device,
                        compute_type=target_compute,
                    )
                except Exception as inner_e:
                    raise ModelError(f"Failed to initialize faster-whisper model on CPU fallback: {str(inner_e)}")
            else:
                raise ModelError(f"Failed to initialize faster-whisper model '{config.model_name}': {str(e)}")

        try:
            segments_gen, info = model.transcribe(
                str(resolved_audio),
                beam_size=config.beam_size,
                temperature=config.temperature,
                language=config.language,
                vad_filter=config.vad_filter,
                word_timestamps=True,
            )

            raw_segments: List[TranscriptSegment] = []
            segment_idx = 0

            for seg in segments_gen:
                seg_words: List[TranscriptWord] = []
                if seg.words:
                    word_idx = 0
                    for w in seg.words:
                        clean_word = w.word.strip()
                        if clean_word:
                            seg_words.append(
                                TranscriptWord(
                                    word_id=word_idx,
                                    word=clean_word,
                                    start_ms=int(round(w.start * 1000)),
                                    end_ms=int(round(w.end * 1000)),
                                    confidence=round(w.probability, 4) if w.probability else 1.0,
                                )
                            )
                            word_idx += 1

                start_ms = int(round(seg.start * 1000))
                end_ms = int(round(seg.end * 1000))

                # Align segment bounds with words if available
                if seg_words:
                    start_ms = min(start_ms, seg_words[0].start_ms)
                    end_ms = max(end_ms, seg_words[-1].end_ms)

                raw_segments.append(
                    TranscriptSegment(
                        segment_id=segment_idx,
                        speaker_id="SPEAKER_00",
                        start_ms=start_ms,
                        end_ms=end_ms,
                        text=seg.text.strip(),
                        avg_confidence=round(seg.avg_logprob, 4) if hasattr(seg, "avg_logprob") else 1.0,
                        words=seg_words,
                    )
                )
                segment_idx += 1

            duration_ms = round((time.time() - t0) * 1000, 2)

            return RawASRResult(
                segments=raw_segments,
                language_detected=info.language or "en",
                language_probability=round(info.language_probability, 4) if info.language_probability else 1.0,
                device_used=target_device,
                compute_type_used=target_compute,
                execution_duration_ms=duration_ms,
            )

        except Exception as e:
            raise ModelError(f"faster-whisper inference failed: {str(e)}")
