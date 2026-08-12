# ASR PROVIDER CONTRACT — LOCAL AI CLIPPER

## 1. Provider Abstraction Interface (`ASRProvider`)
All ASR provider implementations MUST inherit from the abstract base class `ASRProvider`.

```python
class ASRProvider(ABC):
    @abstractmethod
    def transcribe(
        self,
        audio_path: Path,
        config: ASRConfig,
    ) -> RawASRResult:
        """Executes ASR model inference on target PCM audio file."""
        pass
```

## 2. Supported Concrete Providers
1. **`FasterWhisperProvider` (Primary):** Utilizes `faster-whisper` (CTranslate2 C++ backend) for local high-throughput inference with word-level timestamps.
2. **`MockASRProvider` (Testing):** Synthetic ASR generator for unit and integration testing without loading full model weights.

## 3. Configuration Contract (`ASRConfig`)
- `model_name`: `whisper-large-v3`, `whisper-medium`, `whisper-small`, `whisper-base`, `whisper-tiny`
- `device`: `auto`, `cuda`, `cpu`
- `compute_type`: `float16`, `int8_float16`, `int8`, `float32`
- `beam_size`: int (default `5`)
- `temperature`: float (default `0.0`)
- `language`: Optional[str] (e.g. `en`)
- `vad_filter`: bool (default `True`)
