"""
Domain Pydantic Schemas for Local AI Clipper.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict
from clipper.core.state import JobState


class CandidateStatus(str, Enum):
    PROPOSED = "PROPOSED"
    VALIDATED = "VALIDATED"
    SCORED = "SCORED"
    RANKED = "RANKED"
    DUPLICATE = "DUPLICATE"
    REJECTED = "REJECTED"
    SELECTED = "SELECTED"


class QCStatus(str, Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    WARNING = "WARNING"


class CandidateFeatureVector(BaseModel):
    hook_strength: float = 0.5
    curiosity_gap: float = 0.5
    emotional_intensity: float = 0.5
    information_value: float = 0.5
    story_completeness: float = 0.5
    novelty: float = 0.5
    payoff: float = 0.5
    pacing_quality: float = 0.5
    context_independence: float = 0.5
    repetition_penalty: float = 0.0


class ClipScore(BaseModel):
    composite_score: float = 0.0
    hook_score: float = 0.0
    story_score: float = 0.0
    curiosity_score: float = 0.0
    value_score: float = 0.0
    emotion_score: float = 0.0
    pacing_score: float = 0.0
    context_score: float = 0.0
    novelty_score: float = 0.0
    repetition_penalty: float = 0.0
    ai_confidence: float = 1.0


class CandidateProvenance(BaseModel):
    transcript_id: str
    boundary_version: str = "v1.0.0"
    feature_version: str = "v1.0.0"
    scoring_version: str = "v1.0.0"
    llm_provider: str = "MockLLMProvider"
    llm_model: str = "mock-v1"
    prompt_version: str = "v1.0.0"
    config_hash: str = "default_config"


class ClipCandidate(BaseModel):
    model_config = ConfigDict(frozen=False)

    candidate_id: str
    transcript_id: str
    start_ms: int
    end_ms: int
    duration_seconds: float
    text: str
    hook_summary: Optional[str] = None
    score: ClipScore = Field(default_factory=ClipScore)
    feature_vector: CandidateFeatureVector = Field(default_factory=CandidateFeatureVector)
    source_segment_ids: List[int] = Field(default_factory=list)
    provenance: CandidateProvenance
    status: CandidateStatus = CandidateStatus.PROPOSED
    is_selected: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Floor 5 Schemas: Visual Intelligence, Auto-Reframing & Captions

class BoundingBox(BaseModel):
    xmin: float  # 0.0 to 1.0
    ymin: float  # 0.0 to 1.0
    width: float  # 0.0 to 1.0
    height: float  # 0.0 to 1.0
    confidence: float = 1.0
    label: str = "person"


class CropKeyframe(BaseModel):
    timestamp_ms: int
    crop_x: float  # Normalized 0.0 to 1.0
    crop_y: float  # Normalized 0.0 to 1.0
    crop_w: float  # Normalized 0.0 to 1.0
    crop_h: float  # Normalized 0.0 to 1.0
    target_aspect_ratio: str = "9:16"
    is_interpolated: bool = False


class CaptionWord(BaseModel):
    word: str
    start_ms: int
    end_ms: int
    highlight: bool = False


class CaptionSegment(BaseModel):
    segment_id: int
    start_ms: int
    end_ms: int
    text: str
    lines: List[str] = Field(default_factory=list)
    words: List[CaptionWord] = Field(default_factory=list)
    position_vertical: str = "bottom"
    vertical_margin_pct: float = 10.0


class CaptionStyle(BaseModel):
    font_name: str = "Outfit"
    font_size: int = 24
    primary_color: str = "&H00FFFFFF"
    outline_color: str = "&H00000000"
    back_color: str = "&H80000000"
    bold: bool = True
    outline_width: float = 2.0
    alignment: int = 2
    margin_v: int = 40


class CollisionBox(BaseModel):
    bbox_subject: BoundingBox
    bbox_caption: BoundingBox
    overlap_ratio: float
    is_collision: bool = False
    action_taken: str = "none"


class VisualAnalysisResult(BaseModel):
    asset_id: str
    duration_seconds: float
    scene_change_timestamps_ms: List[int] = Field(default_factory=list)
    detected_subjects_count: int = 1
    has_face: bool = True
    avg_subject_confidence: float = 0.95


class RenderPlanProvenance(BaseModel):
    candidate_id: str
    transcript_id: str
    reframing_version: str = "v1.0.0"
    caption_version: str = "v1.0.0"
    collision_version: str = "v1.0.0"
    visual_provider: str = "MediaPipeOrFallback"
    config_hash: str = "default_renderplan_config"


class RenderPlan(BaseModel):
    model_config = ConfigDict(frozen=False)

    plan_id: str
    candidate_id: str
    source_asset_id: str
    start_ms: int
    end_ms: int
    duration_seconds: float
    source_width: int = 1920
    source_height: int = 1080
    target_width: int = 1080
    target_height: int = 1920
    crop_keyframes: List[CropKeyframe] = Field(default_factory=list)
    caption_segments: List[CaptionSegment] = Field(default_factory=list)
    caption_style: CaptionStyle = Field(default_factory=CaptionStyle)
    collisions_resolved: int = 0
    provenance: RenderPlanProvenance
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Floor 6 Schemas: Video Rendering & Quality Control

class QCResult(BaseModel):
    status: QCStatus = QCStatus.PASSED
    ffprobe_valid: bool = True
    video_stream_valid: bool = True
    audio_stream_valid: bool = True
    av_sync_drift_seconds: float = 0.0
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class RenderProfile(BaseModel):
    profile_id: str = "short_1080"
    target_width: int = 1080
    target_height: int = 1920
    fps: float = 30.0
    video_codec: str = "h264"
    pixel_format: str = "yuv420p"
    audio_codec: str = "aac"
    audio_bitrate_kbps: int = 192
    bitrate_kbps: int = 4000
    crf: int = 23
    preset: str = "medium"


class RenderingProvenance(BaseModel):
    render_plan_id: str
    source_asset_id: str
    source_hash: str
    render_plan_hash: str
    output_hash: str
    render_backend: str = "CPU"
    fallback_reason: Optional[str] = None
    render_profile_id: str = "short_1080"
    ffmpeg_version: str = "ffmpeg-master"
    render_duration_ms: float = 0.0
    realtime_factor: float = 0.0


class RenderedAsset(BaseModel):
    model_config = ConfigDict(frozen=False)

    asset_id: str
    plan_id: str
    source_asset_id: str
    file_path: str
    filename: str
    file_hash_sha256: str
    size_bytes: int
    duration_seconds: float
    width: int = 1080
    height: int = 1920
    fps: float = 30.0
    video_codec: str = "h264"
    audio_codec: str = "aac"
    pixel_format: str = "yuv420p"
    qc_result: QCResult = Field(default_factory=QCResult)
    provenance: RenderingProvenance
    created_at: datetime = Field(default_factory=datetime.utcnow)


class RenderJob(BaseModel):
    model_config = ConfigDict(frozen=False)

    render_job_id: str
    manifest_job_id: str
    plan_id: str
    status: JobState = JobState.QUEUED
    render_profile: str = "short_1080"
    render_backend: str = "CPU"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TranscriptWord(BaseModel):
    word_id: Optional[int] = None
    word: str
    start_ms: int
    end_ms: int
    confidence: float = 1.0


class TranscriptSegment(BaseModel):
    segment_id: int
    speaker_id: Optional[str] = None
    start_ms: int
    end_ms: int
    text: str
    avg_confidence: float = 1.0
    words: List[TranscriptWord] = Field(default_factory=list)


class SpeakerInfo(BaseModel):
    speaker_id: str
    label: str = "SPEAKER_00"
    voice_signature_hash: Optional[str] = None


class ASRProvenance(BaseModel):
    asr_provider: str = "FasterWhisperProvider"
    model_name: str = "whisper-large-v3"
    model_version: str = "1.0.0"
    device: str = "cpu"
    compute_type: str = "int8"
    language_requested: Optional[str] = None
    language_detected: Optional[str] = "en"
    language_probability: Optional[float] = 1.0
    execution_duration_ms: float = 0.0
    realtime_factor: float = 0.0
    timestamp_corrections_count: int = 0


class Transcript(BaseModel):
    model_config = ConfigDict(frozen=False)

    transcript_id: str
    asset_id: str
    language: str = "en"
    duration_seconds: float
    segments: List[TranscriptSegment] = Field(default_factory=list)
    speakers: List[SpeakerInfo] = Field(default_factory=list)
    provenance: ASRProvenance = Field(default_factory=ASRProvenance)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    transcript_hash_sha256: Optional[str] = None


class VideoStreamInfo(BaseModel):
    codec: str
    width: int
    height: int
    fps: float
    pixel_format: str = "yuv420p"
    bitrate_kbps: Optional[int] = None
    frame_count: Optional[int] = None
    rotation: int = 0


class AudioStreamInfo(BaseModel):
    codec: str
    sample_rate: int
    channels: int
    channel_layout: Optional[str] = None
    bitrate_kbps: Optional[int] = None
    duration_seconds: Optional[float] = None


class MediaContainerInfo(BaseModel):
    format_name: str
    duration_seconds: float
    size_bytes: int
    bitrate_kbps: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MediaProbeInfo(BaseModel):
    container: MediaContainerInfo
    video: Optional[VideoStreamInfo] = None
    audio: Optional[AudioStreamInfo] = None
    raw_probe_json: Dict[str, Any] = Field(default_factory=dict)


class NormalizationDecision(BaseModel):
    needs_normalization: bool
    reasons: List[str] = Field(default_factory=list)
    target_container: str = "mp4"
    target_video_codec: str = "h264"
    target_audio_codec: str = "aac"
    target_pixel_format: str = "yuv420p"


class MediaAsset(BaseModel):
    model_config = ConfigDict(frozen=False)

    asset_id: str
    source_id: str = "src_default"
    parent_asset_id: Optional[str] = None
    file_path: str
    filename: str
    extension: str
    file_hash_sha256: str
    size_bytes: int
    duration_seconds: float
    video_stream: Optional[VideoStreamInfo] = None
    audio_stream: Optional[AudioStreamInfo] = None
    has_video: bool = True
    has_audio: bool = True
    is_normalized: bool = False
    validation_status: str = "SUPPORTED_VALID"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    tool_version: str = "clipper_v0.1.0"


class StageStatus(BaseModel):
    model_config = ConfigDict(frozen=False)

    stage_name: str
    status: str = "NOT_STARTED"
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    checkpoint_hash: Optional[str] = None


class SourceMediaInfo(BaseModel):
    file_path: str
    file_hash_sha256: str
    file_size_bytes: int
    duration_seconds: float
    width: int
    height: int
    fps: float
    video_codec: str
    audio_codec: str


class SystemEnvironmentInfo(BaseModel):
    python_version: str
    host_os: str
    architecture: str
    cpu_info: str
    ram_gb: float
    disk_free_gb: float
    cuda_available: bool
    gpu_name: Optional[str] = None


class JobManifest(BaseModel):
    model_config = ConfigDict(frozen=False)

    manifest_version: str = "1.0.0"
    job_id: str
    project_id: str = "default"
    status: JobState = JobState.QUEUED
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    source_media: Optional[SourceMediaInfo] = None
    media_asset: Optional[MediaAsset] = None
    normalized_asset: Optional[MediaAsset] = None
    transcript: Optional[Transcript] = None
    candidates: List[ClipCandidate] = Field(default_factory=list)
    render_plan: Optional[RenderPlan] = None
    rendered_asset: Optional[RenderedAsset] = None
    environment: Optional[SystemEnvironmentInfo] = None
    stages: Dict[str, StageStatus] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    checksum_sha256: Optional[str] = None
