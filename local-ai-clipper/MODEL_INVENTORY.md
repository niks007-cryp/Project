# AI MODEL INVENTORY — LOCAL AI CLIPPER

## 1. Automated Speech Recognition (ASR) Models

| Model Name | Version / Architecture | Provider / Engine | License | Execution Target | Fallback Strategy |
|------------|------------------------|-------------------|---------|------------------|-------------------|
| `whisper-large-v3` | CTranslate2 quantized (int8/float16) | `faster-whisper` | MIT | GPU CUDA / CPU | `whisper-medium` |
| `whisper-medium` | CTranslate2 quantized (int8) | `faster-whisper` | MIT | CPU / GPU | `whisper-small` |
| `whisper-small` | CTranslate2 quantized (int8) | `faster-whisper` | MIT | CPU / GPU | `whisper-tiny` |
| `whisper-tiny` | CTranslate2 quantized (int8) | `faster-whisper` | MIT | CPU (Lightweight testing) | None |

## 2. Computer Vision & Subject Tracking Models

| Model Name | Version / Architecture | Provider / Engine | License | Execution Target | Fallback Strategy |
|------------|------------------------|-------------------|---------|------------------|-------------------|
| `MediaPipe Face Detection` | Short/Full Range TFLite | Google MediaPipe | Apache 2.0 | CPU / GPU | OpenCV Cascade |
| `MediaPipe Pose` | BlazePose GHUM | Google MediaPipe | Apache 2.0 | CPU / GPU | Static Center Crop |

## 3. Intelligence & Clip Scoring LLM Providers

| Provider / Model | Interface | Privacy Class | License / Terms | Usage Role |
|------------------|-----------|---------------|-----------------|------------|
| `Ollama / Qwen2.5-7B-Instruct` | Local HTTP API | Local-First (Zero Data Leak) | Apache 2.0 | Hook Scoring & Boundary Analysis |
| `Gemini 2.5 Flash / Pro` | Google GenAI SDK | Cloud API (External) | Google TOS | Optional Cloud Intelligence Provider |
| `OpenAI gpt-4o-mini` | OpenAI REST API | Cloud API (External) | OpenAI TOS | Optional Cloud Intelligence Provider |
