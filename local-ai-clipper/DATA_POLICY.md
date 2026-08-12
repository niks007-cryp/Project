# DATA RETENTION & PRIVACY POLICY — LOCAL AI CLIPPER

## 1. Data Classification

| Data Type | Storage Location | Sensitivity | Retention Default | External Transmission |
|-----------|------------------|-------------|-------------------|-----------------------|
| Source Media | `jobs/<JOB_ID>/input/` | Confidential | Retained until job deletion | NEVER |
| Extracted Audio | `jobs/<JOB_ID>/audio/` | Confidential | Deleted after ASR phase | NEVER |
| Transcript Files | `jobs/<JOB_ID>/transcript/` | Internal | Retained with Job Manifest | Text passed to LLM if external provider selected |
| Model Manifests | `jobs/<JOB_ID>/manifest.json` | Internal | Permanent (Audit Trail) | NEVER |
| Rendered Clips | `jobs/<JOB_ID>/renders/` | Public / Output | Retained until user cleanup | Local Output |

## 2. Secure Cleanup Mechanisms
- **Job Garbage Collection:** Executing `clipper clean --job <JOB_ID>` removes intermediate audio files, temporary frame dumps, and draft ASS subtitles while retaining final renders and the manifest summary.
- **Auto-Purge Threshold:** Disk usage monitor automatically alerts when `N:/local-ai-clipper` free space drops below 15GB.
