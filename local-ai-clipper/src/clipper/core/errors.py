"""
Foundational Error Taxonomy for Local AI Clipper.
"""

from typing import Optional, Any, Dict


class ClipperError(Exception):
    """Base exception class for all Local AI Clipper errors."""
    code: str = "SYSTEM_ERROR"
    retryable: bool = False

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error_type": self.__class__.__name__,
            "code": self.code,
            "message": self.message,
            "retryable": self.retryable,
            "details": self.details,
        }


class UserError(ClipperError):
    """Errors caused by invalid user flags, arguments, or interactions."""
    code = "USER_ERROR"
    retryable = False


class InputError(ClipperError):
    """Errors caused by missing, unreadable, or corrupted input media files."""
    code = "INPUT_ERROR"
    retryable = False


class ValidationError(ClipperError):
    """Errors caused by schema validation or boundary checks failing."""
    code = "VALIDATION_ERROR"
    retryable = False


class TransientError(ClipperError):
    """Temporary errors (e.g. process lock timeouts) that can be safely retried."""
    code = "TRANSIENT_ERROR"
    retryable = True


class ResourceError(ClipperError):
    """Errors caused by resource exhaustion (out of memory, low disk space, VRAM limits)."""
    code = "RESOURCE_ERROR"
    retryable = False


class ModelError(ClipperError):
    """Errors caused by AI/ML model loading or inference failures."""
    code = "MODEL_ERROR"
    retryable = True


class ExternalServiceError(ClipperError):
    """Errors caused by external API provider failures or rate limits."""
    code = "EXTERNAL_SERVICE_ERROR"
    retryable = True


class ExternalProviderNotConfiguredError(UserError):
    """Raised when an external AI API provider is requested but no API key is configured."""
    code = "EXTERNAL_PROVIDER_NOT_CONFIGURED"
    retryable = False


class SystemError(ClipperError):
    """Unexpected internal system or OS runtime failures."""
    code = "SYSTEM_ERROR"
    retryable = False


class SecurityError(ClipperError):
    """Errors caused by path traversal attempts, command injection risks, or invalid bounds."""
    code = "SECURITY_ERROR"
    retryable = False


class InvalidStateTransitionError(ClipperError):
    """Raised when an illegal job state transition is attempted."""
    code = "INVALID_STATE_TRANSITION"
    retryable = False


class ManifestCorruptionError(ClipperError):
    """Raised when a job manifest fails integrity or checksum validation."""
    code = "MANIFEST_CORRUPTED"
    retryable = False


class UnsupportedMediaFormatError(InputError):
    """Raised when input container format or codec is unsupported."""
    code = "UNSUPPORTED_FORMAT"
    retryable = False


class CorruptMediaError(InputError):
    """Raised when media file is truncated, corrupt, or missing required streams."""
    code = "CORRUPTED_MEDIA"
    retryable = False


class FFprobeError(SystemError):
    """Raised when ffprobe execution fails or produces unparseable output."""
    code = "FFPROBE_FAILED"
    retryable = False


class FFmpegError(SystemError):
    """Raised when ffmpeg media processing subprocess fails."""
    code = "FFMPEG_FAILED"
    retryable = True
