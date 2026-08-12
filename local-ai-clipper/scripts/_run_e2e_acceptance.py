"""
End-to-End Acceptance Test Script for Local AI Clipper v1.0.
"""

import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.resolve()
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from clipper.web.api import LocalClipperAPI
from clipper.core.ingestion.youtube import validate_youtube_url
from clipper.infrastructure.security import SecurityError

def run_e2e():
    api = LocalClipperAPI()
    
    print("==================================================")
    print("   V1.0 FINAL E2E ACCEPTANCE GATE EXECUTION       ")
    print("==================================================")
    
    # 1. Pre-flight & Health Check
    health = api.get_health_status()
    print(f"\n[1/7] Local Worker Health: {health['status']} (Mode: {health['mode']})")
    
    # 2. Local File Upload Ingestion (Test A)
    test_video = Path("N:/local-ai-clipper/jobs/job_ingest_sample/sample.mp4")
    if not test_video.exists():
        # Create synthetic test media file
        test_video.parent.mkdir(parents=True, exist_ok=True)
        from tests.fixtures.media_generator import SyntheticMediaGenerator
        SyntheticMediaGenerator.generate_valid_mp4(test_video, duration_sec=5)
    
    print(f"\n[2/7] Test A — Local Video Ingestion: {test_video.name}")
    t0 = time.time()
    local_asset = api.ingest_media(str(test_video), job_id="job_e2e_local_test")
    t_ingest = time.time() - t0
    print(f"   MediaAsset ID: {local_asset['asset_id']}")
    print(f"   Duration: {local_asset['duration_seconds']}s | Size: {local_asset['size_bytes']} bytes")
    print(f"   Validation Status: {local_asset['validation_status']}")
    print(f"   Ingestion Time: {t_ingest:.2f}s")
    
    # 3. YouTube URL Ingestion (Test B)
    yt_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    print(f"\n[3/7] Test B — YouTube Acquisition: {yt_url}")
    t0 = time.time()
    yt_asset = api.ingest_youtube(yt_url, job_id="job_e2e_yt_test")
    t_yt = time.time() - t0
    print(f"   MediaAsset ID: {yt_asset['asset_id']}")
    print(f"   Duration: {yt_asset['duration_seconds']}s | Size: {yt_asset['size_bytes']} bytes")
    print(f"   Acquisition + Ingestion Time: {t_yt:.2f}s")
    
    # 4. Pipeline Execution: Transcription -> Candidates -> RenderPlan -> Render & QC
    print(f"\n[4/7] Pipeline Execution (Transcription, Intelligence, Reframing, Rendering, QC)")
    job_id = "job_e2e_yt_test"
    
    # Stage 1: Transcribe
    t0 = time.time()
    tx = api.run_pipeline_stage(job_id, "transcribe", {"mock": True})
    t_tx = time.time() - t0
    print(f"   [Floor 3 ASR] Transcript ID: {tx['transcript_id']} ({len(tx['segments'])} segments) [{t_tx:.2f}s]")
    
    # Stage 2: Clip Candidates
    t0 = time.time()
    cands = api.run_pipeline_stage(job_id, "candidates", {"min_duration": 3.0, "top_k": 3})
    t_cand = time.time() - t0
    top_score = cands[0]["score"]["composite_score"] if cands else 0.0
    print(f"   [Floor 4 LLM] Clip Candidates: {len(cands)} generated (Top Score: {top_score:.2f}) [{t_cand:.2f}s]")
    
    # Stage 3: Reframing & RenderPlan
    t0 = time.time()
    plan = api.run_pipeline_stage(job_id, "renderplan", {})
    t_plan = time.time() - t0
    print(f"   [Floor 5 CV] RenderPlan ID: {plan['plan_id']} ({plan['target_width']}x{plan['target_height']} 9:16) [{t_plan:.2f}s]")
    
    # Stage 4: Video Rendering & Quality Control
    t0 = time.time()
    rendered = api.run_pipeline_stage(job_id, "render", {"profile": "preview"})
    t_rnd = time.time() - t0
    qc_status = rendered["qc_result"]["status"]
    print(f"   [Floor 6 Render & QC] Rendered Asset ID: {rendered['asset_id']}")
    print(f"   Output File: {rendered['filename']} | Hash: {rendered['file_hash_sha256'][:16]}...")
    print(f"   QC Status: {qc_status} [{t_rnd:.2f}s]")
    
    # 5. Security & SSRF Validation Test
    print(f"\n[5/7] SSRF & Security Rejection Test")
    invalid_url = "https://localhost/admin"
    try:
        validate_youtube_url(invalid_url)
        print("   FAIL: SSRF rejection did not throw expected exception")
    except SecurityError as se:
        print(f"   PASS: Successfully rejected SSRF primitive ({se})")
    
    # 6. BYOK Credential Vault Test
    print(f"\n[6/7] BYOK Credential Vault Check")
    providers = api.list_providers()
    for p in providers:
        print(f"   Provider: {p['provider_name'].upper()} | Configured: {p['is_configured']} | Key: {p['api_key_masked']}")
    
    # 7. Summary
    print("\n[7/7] Acceptance Execution Complete.")
    print("==================================================")

if __name__ == "__main__":
    run_e2e()
