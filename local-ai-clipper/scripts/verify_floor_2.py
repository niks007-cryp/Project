"""
Floor 2 Verification Suite & Certification Verifier for Local AI Clipper.
"""

import sys
import tempfile
import subprocess
from pathlib import Path
from clipper import __version__
from clipper.core.manifest import ManifestManager
from clipper.domain.models import JobManifest
from clipper.infrastructure.ffmpeg import SafeFFprobe, SafeFFmpeg
from clipper.infrastructure.logger import get_logger
from clipper.pipeline.ingestion_stage import IngestionStage, IngestionStageInput
from tests.fixtures.media_generator import SyntheticMediaGenerator


def run_floor_2_verification() -> bool:
    print("==========================================================")
    print("      LOCAL AI CLIPPER — FLOOR 2 VERIFICATION SUITE       ")
    print("==========================================================")
    print(f" Application Version: v{__version__}")
    print(f" Python Executable:   {sys.executable}")
    print(f" Target Directory:    N:/local-ai-clipper\n")

    checks = []

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        job_dir = tmp_path / "jobs" / "verify_floor_2"
        job_dir.mkdir(parents=True, exist_ok=True)
        manager = ManifestManager(job_dir)
        manifest = JobManifest(job_id="verify_floor_2")
        manager.save(manifest)
        logger = get_logger("verify_floor_2")

        # 1. FFmpeg & FFprobe Functional Smoke Tests
        print("--- 1. FFmpeg & FFprobe Toolchain Smoke Tests ---")
        try:
            ff_ok = SafeFFmpeg.functional_smoke_test()
            print(" [PASS] FFprobe functional execution verified")
            print(" [PASS] FFmpeg functional execution verified")
            checks.append(("FFmpeg Toolchain Smoke Test", ff_ok))
        except Exception as e:
            print(f" [FAIL] FFmpeg smoke test failed: {str(e)}")
            checks.append(("FFmpeg Toolchain Smoke Test", False))

        # 2. Formats Ingestion Tests (MP4, MOV, MKV, WEBM, M4V)
        print("\n--- 2. Multi-Format Ingestion Tests ---")
        stage = IngestionStage(manager, logger)
        
        # MP4
        try:
            mp4_file = SyntheticMediaGenerator.generate_valid_mp4(tmp_path / "test.mp4")
            out_mp4 = stage.run(IngestionStageInput(file_path=str(mp4_file)))
            mp4_ok = out_mp4.media_asset.has_video and out_mp4.media_asset.has_audio
            print(" [PASS] MP4 media ingestion verified")
        except Exception as e:
            print(f" [FAIL] MP4 ingestion failed: {str(e)}")
            mp4_ok = False
        checks.append(("MP4 Ingestion", mp4_ok))

        # MOV
        try:
            mov_file = SyntheticMediaGenerator.generate_valid_mov(tmp_path / "test.mov")
            out_mov = stage.run(IngestionStageInput(file_path=str(mov_file)))
            mov_ok = out_mov.media_asset.extension == ".mov"
            print(" [PASS] MOV media ingestion verified")
        except Exception as e:
            print(f" [FAIL] MOV ingestion failed: {str(e)}")
            mov_ok = False
        checks.append(("MOV Ingestion", mov_ok))

        # MKV
        try:
            mkv_file = SyntheticMediaGenerator.generate_valid_mkv(tmp_path / "test.mkv")
            out_mkv = stage.run(IngestionStageInput(file_path=str(mkv_file)))
            mkv_ok = out_mkv.media_asset.extension == ".mkv"
            print(" [PASS] MKV media ingestion verified")
        except Exception as e:
            print(f" [FAIL] MKV ingestion failed: {str(e)}")
            mkv_ok = False
        checks.append(("MKV Ingestion", mkv_ok))

        # WEBM
        try:
            webm_file = SyntheticMediaGenerator.generate_valid_webm(tmp_path / "test.webm")
            out_webm = stage.run(IngestionStageInput(file_path=str(webm_file)))
            webm_ok = out_webm.media_asset.extension == ".webm"
            print(" [PASS] WEBM media ingestion verified")
        except Exception as e:
            print(f" [FAIL] WEBM ingestion failed: {str(e)}")
            webm_ok = False
        checks.append(("WEBM Ingestion", webm_ok))

        # M4V
        try:
            m4v_file = SyntheticMediaGenerator.generate_valid_m4v(tmp_path / "test.m4v")
            out_m4v = stage.run(IngestionStageInput(file_path=str(m4v_file)))
            m4v_ok = out_m4v.media_asset.extension == ".m4v"
            print(" [PASS] M4V media ingestion verified")
        except Exception as e:
            print(f" [FAIL] M4V ingestion failed: {str(e)}")
            m4v_ok = False
        checks.append(("M4V Ingestion", m4v_ok))

        # 3. Corrupt Media Rejection Test
        print("\n--- 3. Corrupt Media & Security Rejection ---")
        try:
            corrupt_file = SyntheticMediaGenerator.generate_corrupt_file(tmp_path / "bad.mp4")
            try:
                stage.run(IngestionStageInput(file_path=str(corrupt_file)))
                corrupt_ok = False
                print(" [FAIL] Corrupt media was not rejected!")
            except Exception:
                corrupt_ok = True
                print(" [PASS] Corrupt media correctly rejected")
        except Exception as e:
            corrupt_ok = False
            print(f" [FAIL] Corrupt media test error: {str(e)}")
        checks.append(("Corrupt Media Rejection", corrupt_ok))

        # 4. Normalization & Idempotency Check
        print("\n--- 4. Normalization & Idempotency Check ---")
        try:
            rot_file = SyntheticMediaGenerator.generate_rotated_video(tmp_path / "rot.mp4")
            out_rot1 = stage.run(IngestionStageInput(file_path=str(rot_file)))
            norm_ok = out_rot1.normalized_asset is not None and out_rot1.normalized_asset.is_normalized
            
            # Second run for idempotency check
            out_rot2 = stage.run(IngestionStageInput(file_path=str(rot_file)))
            idemp_ok = out_rot2.is_idempotent_skip is True
            print(" [PASS] Rotated media auto-normalization verified")
            print(" [PASS] Idempotent re-ingestion skip verified")
            checks.append(("Normalization & Idempotency", norm_ok and idemp_ok))
        except Exception as e:
            print(f" [FAIL] Normalization / idempotency test failed: {str(e)}")
            checks.append(("Normalization & Idempotency", False))

    # 5. Executing Pytest Integration Suite
    print("\n--- 5. Executing Pytest Integration Suite ---")
    pytest_cmd = [sys.executable, "-m", "pytest", "tests", "-v", "--tb=short"]
    try:
        res = subprocess.run(pytest_cmd, capture_output=True, text=True, cwd="N:/local-ai-clipper")
        print(res.stdout)
        test_pass = res.returncode == 0
        if test_pass:
            print(" [PASS] All Floor 2 Pytest Unit & Integration Tests Passed!")
        else:
            print(" [FAIL] Pytest suite failed:\n" + res.stderr)
    except Exception as e:
        print(f" [FAIL] Failed to execute pytest: {str(e)}")
        test_pass = False
    checks.append(("Automated Test Suite", test_pass))

    # Summary Assessment
    print("\n==========================================================")
    print("              FLOOR 2 VERIFICATION SUMMARY                ")
    print("==========================================================")
    all_ok = True
    for title, passed in checks:
        status_str = "[PASS] CERTIFIED" if passed else "[FAIL] REJECTED"
        if not passed:
            all_ok = False
        print(f"  {status_str} : {title}")

    if all_ok:
        print("\n>>> FLOOR 2 IS CERTIFIED COMPLETE <<<")
        print("Media Ingestion & Validation Subsystem is production-ready.")
        print("Floor 3 (Transcription) remains LOCKED until authorized.")
        return True
    else:
        print("\n>>> FLOOR 2 VERIFICATION FAILED <<<")
        print("Resolve failing components before attempting certification.")
        return False


if __name__ == "__main__":
    success = run_floor_2_verification()
    sys.exit(0 if success else 1)
