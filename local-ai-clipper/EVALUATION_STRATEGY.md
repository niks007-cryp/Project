# AI EVALUATION STRATEGY — LOCAL AI CLIPPER

## 1. Benchmarking Principles
AI evaluations MUST NOT rely on anecdotal human inspection ("looks good"). Quantitative benchmarks and reference ground-truth datasets are required for key AI subsystems.

## 2. Quantitative Evaluation Metrics

### 2.1 ASR Quality (Transcription)
- **Word Error Rate (WER):** Target `<= 5.0%` on clean speech test dataset.
- **Timestamp Accuracy:** Mean Start/End Delta Target `<= 150ms` against human-aligned audio ground truth.

### 2.2 Clip Intelligence (Hook Selection)
- **Precision @ K (K=3):** Target `>= 80%` overlap between top 3 LLM-selected clips and human editor curated gold-standard clips.
- **Truncation Rate:** Target `0.0%` (Zero clips cut mid-word or mid-sentence).
- **Duplicate Rate:** Target `0.0%` near-identical clip candidate outputs.

### 2.3 Reframing & Vision Tracking
- **Face Visibility Rate:** Target `>= 95%` frame duration with speaker face positioned within 9:16 active framing bounds.
- **Bounding Box Jitter (Framing Instability):** Smooth trajectory derivative metric `< 5%` frame-over-frame displacement variance.

## 3. Regression Testing Framework
Changes to LLM scoring prompts or CV tracking parameters MUST trigger regression benchmark runs against the standard evaluation dataset before PR merging.
