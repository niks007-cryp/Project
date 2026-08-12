# FLOOR 2 MEDIA CONTRACT — LOCAL AI CLIPPER

## 1. Scope & Objective
Floor 2 provides a production-grade, local video ingestion, security validation, media probing, normalization, and hashing subsystem. The output of Floor 2 is the immutable `MediaAsset` contract consumed by downstream stages.

## 2. Ingestion Flow Lifecycle
```
INPUT FILE ──► Security Validation ──► FFprobe Analysis ──► Media Validation
                                                                    │
  ┌─────────────────────────────────────────────────────────────────┘
  ▼
Normalization Decision ──► FFmpeg Normalization (If Needed) ──► SHA256 Hashing ──► MediaAsset Manifest Checkpoint
```

## 3. Media Format Support Matrix

| Container / Extension | Video Codec Support | Audio Codec Support | Validation Status |
|-----------------------|---------------------|---------------------|-------------------|
| **MP4** (`.mp4`)      | H.264, HEVC, VP9, AV1 | AAC, MP3, Opus, PCM | Primary Native |
| **MOV** (`.mov`)      | H.264, ProRes, HEVC | AAC, PCM, MP3       | Primary Native |
| **MKV** (`.mkv`)      | H.264, HEVC, VP9, AV1 | AAC, Opus, Vorbis, FLAC | Primary Native |
| **WEBM** (`.webm`)    | VP8, VP9, AV1       | Opus, Vorbis        | Primary Native |
| **M4V** (`.m4v`)      | H.264, HEVC          | AAC, AC3            | Primary Native |

## 4. Media Asset Contract Schema (`MediaAsset`)
- **`asset_id`**: SHA256 content hash prefix (`asset_<hash[:16]>`)
- **`source_id`**: Associated source identifier
- **`parent_asset_id`**: Reference to parent asset if derived/normalized
- **`file_path`**: Absolute path on local filesystem
- **`file_hash_sha256`**: Complete SHA256 string
- **`size_bytes`**: File size on disk
- **`duration_seconds`**: Media stream duration
- **`container_format`**: Verified format name (e.g. `mov,mp4,m4a,3gp,3g2,mj2`)
- **`video_stream`**: `VideoStreamInfo` payload (codec, width, height, fps, pix_fmt, rotation)
- **`audio_stream`**: `AudioStreamInfo` payload (codec, sample_rate, channels, bitrate)
- **`has_audio`**: Boolean flag indicating audio presence
- **`has_video`**: Boolean flag indicating video presence
- **`is_normalized`**: Boolean flag indicating whether normalization was applied
- **`validation_status`**: `SUPPORTED_VALID`, `SUPPORTED_INVALID`, `UNSUPPORTED_FORMAT`, `CORRUPTED_MEDIA`

## 5. Error Taxonomy Additions
- `ERR_MEDIA_SECURITY_REJECTED`: Path traversal, unreadable file, or file size limits exceeded.
- `ERR_UNSUPPORTED_CONTAINER`: Unrecognized or unsupported file format.
- `ERR_CORRUPT_MEDIA`: Truncated, un-parseable, or invalid media streams.
- `ERR_NO_VIDEO_STREAM`: File lacks a usable video track.
- `ERR_FFPROBE_FAILED`: Subprocess execution of `ffprobe` returned non-zero exit code.
- `ERR_FFMPEG_NORMALIZATION_FAILED`: Subprocess execution of `ffmpeg` normalization failed.
