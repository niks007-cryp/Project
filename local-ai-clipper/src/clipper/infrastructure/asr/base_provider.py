"""
ASR Provider Base Abstraction for Local AI Clipper.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from clipper.domain.models import TranscriptSegment, TranscriptWord


class ASRConfig(BaseModel):
    model_name: str = "whisper-tiny"  # whisper-tiny, whisper-base, whisper-small, whisper-medium, whisper-large-v3
    device: str = "auto"  # auto, cuda, cpu
    compute_type: str = "auto"  # auto, float16, int8_float16, int8, float32
    beam_size: int = 5
    temperature: float = 0.0
    language: Optional[str] = None
    vad_filter: bool = True


class RawASRResult(BaseModel):
    segments: List[TranscriptSegment]
    language_detected: str
    language_probability: float
    device_used: str
    compute_type_used: str
    execution_duration_ms: float


class ASRProvider(ABC):
    """Abstract Base Class for ASR Provider implementations."""

    @abstractmethod
    def transcribe(self, audio_path: Path, config: ASRConfig) -> RawASRResult:
        """Executes ASR inference on target audio file."""
        pass
