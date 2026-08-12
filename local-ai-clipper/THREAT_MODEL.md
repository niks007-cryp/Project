# THREAT MODEL — LOCAL AI CLIPPER

## 1. Threat Matrix & Attack Vectors

| Threat ID | Threat Description | Attack Vector | Severity | Mitigation Strategy |
|-----------|--------------------|---------------|----------|---------------------|
| **TM-01** | Command Injection via Media Metadata | Malicious video title/filename containing shell escapes injected into FFmpeg command line. | CRITICAL | Shell string execution forbidden (`shell=True` prohibited). Direct list-based argument arrays used exclusively. |
| **TM-02** | Path Traversal / Arbitrary File Read/Write | Filename parameter containing `../` or absolute paths targeting system directories. | HIGH | Strict path validation & normalization using `Path.resolve()`. Sandbox all writes inside job output directory. |
| **TM-03** | Malicious Media File Exploit / Buffer Overflow | Crafted video file exploiting container/codec vulnerability in FFmpeg parser. | HIGH | Pre-validate container metadata using `ffprobe` with safety limits; isolate media sub-processes with timeouts. |
| **TM-04** | API Key Leakage | Exposing cloud AI keys in logs, stack traces, or version-controlled files. | CRITICAL | Store API keys in environment variables or secured local secrets store. Mask sensitive environment variables in log output. |
| **TM-05** | Storage / VRAM Resource Exhaustion (DoS) | Unbounded batch processing exhausting GPU VRAM or disk space on target drive. | MEDIUM | Disk space checks before queuing (`>20GB` free required); enforce single-task GPU locks and VRAM offloading. |
| **TM-06** | Malformed LLM Prompt Injection | Transcript text containing instructions aimed at subverting LLM structured output. | MEDIUM | Enforce strict Pydantic JSON schema parsing; reject non-conforming responses; sandbox model capabilities. |

## 2. Security Perimeter Boundaries
- **Trust Zone 0:** Host OS and core application engine.
- **Trust Zone 1:** External FFmpeg and CV subprocess invocations (Untrusted binary execution sandbox).
- **Trust Zone 2:** External Cloud API endpoints (Untrusted network boundary).
