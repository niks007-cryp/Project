# CONTENT RIGHTS & COPYRIGHT POLICY — LOCAL AI CLIPPER

## 1. Compliance Principles
- **CR-01 User Responsibility:** Local AI Clipper is designed as a content processing tool for creators who possess valid legal rights, licenses, or explicit authorization to process and edit their media.
- **CR-02 No Circumvention:** The system DOES NOT contain functionality to bypass Digital Rights Management (DRM), decrypt protected media, or circumvent video platform access controls.
- **CR-03 Provenance Metadata:** Every processed job MUST record provenance fields in `job_manifest.json`:
  - `owner_creator_name` (optional user entry)
  - `permission_status` (`AUTHORIZED`, `ORIGINAL_CREATOR`, `FAIR_USE_EVALUATED`, `UNKNOWN`)
  - `source_location` (local path / URI)
  - `rights_notes`

## 2. Authorization Enforcement
- If an input file is explicitly tagged with restrictive rights metadata or missing authorization flags during batch enterprise processing, the system MUST flag the job for manual review prior to rendering.
