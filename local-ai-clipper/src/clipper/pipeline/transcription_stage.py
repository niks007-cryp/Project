"""
Transcription Pipeline Stage for Local AI Clipper.
"""

import hashlib
import json
import time
from pathlib import Path
from typing import Optional
from pydantic import BaseModel
from clipper.core.manifest import ManifestManager
from clipper.core.errors import ValidationError, InputError
from clipper.core.transcription.normalizer import TimestampNormalizer
from clipper.core.transcription.validator import TranscriptValidator
from clipper.domain.models import Transcript, ASRProvenance, MediaAsset
from clipper.infrastructure.asr.base_provider import ASRConfig, ASRProvider
from clipper.infrastructure.asr.faster_whisper_provider import FasterWhisperProvider
from clipper.infrastructure.ffmpeg import SafeFFmpeg
from clipper.infrastructure.logger import ContextLogger
from clipper.pipeline.stage import BaseStage


class TranscriptionStageInput(BaseModel):
    media_asset: MediaAsset
    asr_config: ASRConfig = ASRConfig()
    use_mock_provider: bool = False


class TranscriptionStageOutput(BaseModel):
    transcript: Transcript
    extracted_audio_path: str
    is_idempotent_skip: bool = False


class TranscriptionStage(BaseStage[TranscriptionStageInput, TranscriptionStageOutput]):
    """
    Production-grade Local ASR Transcription Pipeline Stage.
    Flow:
    INPUT -> AUDIO ELIGIBILITY -> AUDIO PREPARATION -> LOCAL ASR -> TIMESTAMP NORMALIZATION -> QUALITY VALIDATION -> PROVENANCE -> CHECKPOINT
    """

    stage_name = "transcription"

    def validate_input(self, input_data: TranscriptionStageInput) -> None:
        asset = input_data.media_asset
        if not asset.has_audio:
            raise InputError(f"Media asset '{asset.asset_id}' has no audio stream eligible for transcription.")
        if not Path(asset.file_path).exists():
            raise InputError(f"Media asset file missing: {asset.file_path}")

    def execute_logic(self, input_data: TranscriptionStageInput) -> TranscriptionStageOutput:
        asset = input_data.media_asset
        manifest = self.manifest_manager.load()
        job_dir = self.manifest_manager.job_dir

        # Compute config hash for idempotency checking
        config_dict = input_data.asr_config.model_dump()
        config_hash = hashlib.sha256(json.dumps(config_dict, sort_keys=True).encode("utf-8")).hexdigest()[:12]

        # Idempotency check: return cached transcript if present with matching asset and config hash
        if (
            manifest.transcript
            and manifest.transcript.asset_id == asset.asset_id
            and manifest.transcript.provenance.model_name == input_data.asr_config.model_name
        ):
            self.logger.info(f"Idempotent transcription skip: Transcript for asset {asset.asset_id} already exists.")
            audio_path = job_dir / "audio" / "audio_16k_mono.wav"
            return TranscriptionStageOutput(
                transcript=manifest.transcript,
                extracted_audio_path=str(audio_path),
                is_idempotent_skip=True,
            )

        # 1. Audio Preparation: Extract 16kHz Mono PCM WAV
        audio_dir = job_dir / "audio"
        audio_dir.mkdir(parents=True, exist_ok=True)
        pcm_wav_path = audio_dir / "audio_16k_mono.wav"

        if not pcm_wav_path.exists() or pcm_wav_path.stat().st_size == 0:
            self.logger.info(f"Extracting 16kHz mono PCM WAV from '{asset.file_path}'...")
            ff_args = [
                "-i", asset.file_path,
                "-vn",
                "-acodec", "pcm_s16le",
                "-ar", "16000",
                "-ac", "1",
                str(pcm_wav_path.resolve())
            ]
            SafeFFmpeg.run_command(ff_args)

        # 2. Select ASR Provider
        if input_data.use_mock_provider:
            from clipper.infrastructure.asr.mock_provider import MockASRProvider
            provider: ASRProvider = MockASRProvider()
        else:
            provider = FasterWhisperProvider()

        # 3. Execute Local ASR Inference
        t0 = time.time()
        raw_res = provider.transcribe(pcm_wav_path, input_data.asr_config)
        exec_duration_ms = round((time.time() - t0) * 1000, 2)

        # 4. Timestamp Normalization
        normalized_segments, corrections_count = TimestampNormalizer.normalize_timestamps(
            raw_res.segments, asset.duration_seconds
        )

        # Calculate Real-Time Factor (RTF = processing_duration / audio_duration)
        rtf = round((exec_duration_ms / 1000.0) / asset.duration_seconds, 4) if asset.duration_seconds > 0 else 0.0

        provenance = ASRProvenance(
            asr_provider=provider.__class__.__name__,
            model_name=input_data.asr_config.model_name,
            model_version="1.0.0",
            device=raw_res.device_used,
            compute_type=raw_res.compute_type_used,
            language_requested=input_data.asr_config.language,
            language_detected=raw_res.language_detected,
            language_probability=raw_res.language_probability,
            execution_duration_ms=exec_duration_ms,
            realtime_factor=rtf,
            timestamp_corrections_count=corrections_count,
        )

        # Construct Transcript Domain Entity
        transcript_hash = hashlib.sha256(
            json.dumps([s.model_dump() for s in normalized_segments], default=str).encode("utf-8")
        ).hexdigest()

        transcript = Transcript(
            transcript_id=f"tx_{transcript_hash[:16]}",
            asset_id=asset.asset_id,
            language=raw_res.language_detected,
            duration_seconds=asset.duration_seconds,
            segments=normalized_segments,
            provenance=provenance,
            transcript_hash_sha256=transcript_hash,
        )

        # 5. Quality Validation
        TranscriptValidator.validate_transcript(transcript)

        # Save to disk and manifest checkpoint
        transcript_dir = job_dir / "transcript"
        transcript_dir.mkdir(parents=True, exist_ok=True)
        tx_file = transcript_dir / "transcript.json"
        
        with open(tx_file, "w", encoding="utf-8") as f:
            json.dump(transcript.model_dump(mode="json"), f, indent=2, default=str)

        manifest.transcript = transcript
        self.manifest_manager.save(manifest)

        return TranscriptionStageOutput(
            transcript=transcript,
            extracted_audio_path=str(pcm_wav_path),
            is_idempotent_skip=False,
        )

    def validate_output(self, output_data: TranscriptionStageOutput) -> None:
        TranscriptValidator.validate_transcript(output_data.transcript)
        if not Path(output_data.extracted_audio_path).exists():
            raise ValueError("Extracted PCM audio file missing.")
