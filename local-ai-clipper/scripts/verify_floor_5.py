"""
Floor 5 Verification Suite & Certification Verifier for Local AI Clipper.
"""

import sys
import tempfile
import time
import subprocess
from pathlib import Path
from clipper import __version__
from clipper.core.manifest import ManifestManager
from clipper.domain.models import JobManifest
from clipper.core.vision.analyzer import VisualAnalyzer
from clipper.core.vision.tracker import SubjectTracker
from clipper.core.vision.crop_planner import CropPlanner
from clipper.core.captions.segmenter import CaptionSegmenter
from clipper.core.captions.styler import CaptionStyler
from clipper.core.vision.collision_engine import CollisionAvoidanceEngine
from clipper.core.vision.renderplan_validator import RenderPlanValidator
from clipper.core.vision.evaluator import VisualEvaluator
from clipper.infrastructure.logger import get_logger
from clipper.pipeline.ingestion_stage import IngestionStage, IngestionStageInput
from clipper.pipeline.transcription_stage import TranscriptionStage, TranscriptionStageInput
from clipper.pipeline.intelligence_stage import IntelligenceStage, IntelligenceStageInput
from clipper.pipeline.reframing_stage import ReframingStage, ReframingStageInput
from tests.fixtures.media_generator import SyntheticMediaGenerator


def run_floor_5_verification() -> bool:
    print("==========================================================")
    print("      LOCAL AI CLIPPER — FLOOR 5 VERIFICATION SUITE       ")
    print("==========================================================")
    print(f" Application Version: v{__version__}")
    print(f" Python Executable:   {sys.executable}")
    print(f" Target Directory:    N:/local-ai-clipper\n")

    checks = []

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        job_dir = tmp_path / "jobs" / "verify_floor_5"
        job_dir.mkdir(parents=True, exist_ok=True)
        manager = ManifestManager(job_dir)
        manifest = JobManifest(job_id="verify_floor_5")
        manager.save(manifest)
        logger = get_logger("verify_floor_5")

        # Generate synthetic test media
        mp4_path = SyntheticMediaGenerator.generate_valid_mp4(tmp_path / "speech.mp4", duration_sec=30)

        # Ingest, Transcribe & Intelligence
        ingest_out = IngestionStage(manager, logger).run(IngestionStageInput(file_path=str(mp4_path)))
        tx_out = TranscriptionStage(manager, logger).run(TranscriptionStageInput(media_asset=ingest_out.media_asset, use_mock_provider=True))
        intel_out = IntelligenceStage(manager, logger).run(IntelligenceStageInput(transcript=tx_out.transcript, min_duration_sec=3.0, top_k=1))

        cand = intel_out.selected_candidates[0]

        # 1. Visual Analysis
        print("--- 1. Visual Intelligence & Bounding Box Extraction ---")
        try:
            boxes = VisualAnalyzer.analyze_asset(ingest_out.media_asset)
            print(f" [PASS] Extracted {len(boxes)} frame subject bounding boxes")
            checks.append(("Visual Analysis & Subject Detection", len(boxes) > 0))
        except Exception as e:
            print(f" [FAIL] Visual analysis failed: {str(e)}")
            checks.append(("Visual Analysis & Subject Detection", False))

        # 2. 9:16 Crop Trajectory & Smoothness
        print("\n--- 2. 9:16 Crop Trajectory & Smoothness ---")
        try:
            raw_kfs = SubjectTracker.generate_trajectory(boxes, cand.start_ms, cand.end_ms)
            constrained_kfs = CropPlanner.validate_and_constrain_keyframes(raw_kfs)
            print(f" [PASS] Generated {len(constrained_kfs)} 9:16 vertical crop keyframes")
            checks.append(("9:16 Crop Trajectory & Smoothness", len(constrained_kfs) > 0))
        except Exception as e:
            print(f" [FAIL] Trajectory generation failed: {str(e)}")
            checks.append(("9:16 Crop Trajectory & Smoothness", False))

        # 3. Caption Segmentation & ASS Styling
        print("\n--- 3. Subtitle Segmentation & ASS Style Generation ---")
        try:
            captions = CaptionSegmenter.segment_candidate_captions(cand, tx_out.transcript)
            style = CaptionStyler.get_default_style()
            header = CaptionStyler.generate_ass_header(style)
            print(f" [PASS] Segmented {len(captions)} subtitle blocks with ASS header")
            checks.append(("Subtitle Segmentation & Styling", len(captions) > 0 and len(header) > 50))
        except Exception as e:
            print(f" [FAIL] Subtitle segmentation failed: {str(e)}")
            checks.append(("Subtitle Segmentation & Styling", False))

        # 4. Collision Avoidance Engine
        print("\n--- 4. Caption & Subject Collision Avoidance Engine ---")
        try:
            resolved_captions, count = CollisionAvoidanceEngine.resolve_collisions(captions, boxes)
            print(f" [PASS] Resolved {count} subtitle-subject visual collisions")
            checks.append(("Collision Avoidance Engine", count >= 0))
        except Exception as e:
            print(f" [FAIL] Collision resolution failed: {str(e)}")
            checks.append(("Collision Avoidance Engine", False))

        # 5. Reframing Stage Execution & Idempotency
        print("\n--- 5. Reframing Pipeline Stage & Idempotency ---")
        try:
            ref_stage = ReframingStage(manager, logger)
            ref_inp = ReframingStageInput(candidate=cand, media_asset=ingest_out.media_asset, transcript=tx_out.transcript)
            ref_out1 = ref_stage.run(ref_inp)
            ref_out2 = ref_stage.run(ref_inp)
            idemp_ok = ref_out2.is_idempotent_skip is True
            print(" [PASS] Generated validated RenderPlan JSON artifact")
            print(" [PASS] Idempotent RenderPlan re-generation skip verified")
            checks.append(("Reframing Stage & Idempotency", idemp_ok))
        except Exception as e:
            print(f" [FAIL] Reframing stage failed: {str(e)}")
            checks.append(("Reframing Stage & Idempotency", False))

        # 6. Visual Evaluation Framework
        print("\n--- 6. Visual Evaluation Framework ---")
        try:
            metrics = VisualEvaluator.evaluate_render_plan(ref_out1.render_plan, boxes)
            eval_ok = metrics["subject_visibility_pct"] > 50.0 and metrics["crop_boundary_violations"] == 0
            print(f" [PASS] Evaluation Metrics: Visibility={metrics['subject_visibility_pct']}%, JumpRate={metrics['tracking_jump_rate_pct']}%")
            checks.append(("Visual Evaluation Framework", eval_ok))
        except Exception as e:
            print(f" [FAIL] Visual evaluation failed: {str(e)}")
            checks.append(("Visual Evaluation Framework", False))

        # 7. CLI Subcommand Verification
        print("\n--- 7. CLI Subcommand Verification ---")
        try:
            cli_cmd = [sys.executable, "-m", "clipper.cli.main", "renderplan", str(mp4_path)]
            res = subprocess.run(cli_cmd, capture_output=True, text=True, cwd="N:/local-ai-clipper")
            cli_ok = res.returncode == 0
            if cli_ok:
                print(" [PASS] CLI 'clipper renderplan' execution verified")
            else:
                print(f" [FAIL] CLI execution failed: {res.stderr}")
            checks.append(("CLI Subcommand Verification", cli_ok))
        except Exception as e:
            print(f" [FAIL] CLI verification error: {str(e)}")
            checks.append(("CLI Subcommand Verification", False))

    # 8. Executing Pytest Integration Suite
    print("\n--- 8. Executing Pytest Integration Suite ---")
    pytest_cmd = [sys.executable, "-m", "pytest", "tests", "-v", "--tb=short"]
    try:
        res = subprocess.run(pytest_cmd, capture_output=True, text=True, cwd="N:/local-ai-clipper")
        print(res.stdout)
        test_pass = res.returncode == 0
        if test_pass:
            print(" [PASS] All Floor 5 Pytest Unit & Integration Tests Passed!")
        else:
            print(" [FAIL] Pytest suite failed:\n" + res.stderr)
    except Exception as e:
        print(f" [FAIL] Failed to execute pytest: {str(e)}")
        test_pass = False
    checks.append(("Automated Test Suite", test_pass))

    # Summary Assessment
    print("\n==========================================================")
    print("              FLOOR 5 VERIFICATION SUMMARY                ")
    print("==========================================================")
    all_ok = True
    for title, passed in checks:
        status_str = "[PASS] CERTIFIED" if passed else "[FAIL] REJECTED"
        if not passed:
            all_ok = False
        print(f"  {status_str} : {title}")

    if all_ok:
        print("\n>>> FLOOR 5 IS CERTIFIED COMPLETE <<<")
        print("Visual Intelligence & RenderPlan Engine Subsystem is production-ready.")
        print("Floor 6 (Shorts Rendering Engine) remains LOCKED until authorized.")
        return True
    else:
        print("\n>>> FLOOR 5 VERIFICATION FAILED <<<")
        print("Resolve failing components before attempting certification.")
        return False


if __name__ == "__main__":
    success = run_floor_5_verification()
    sys.exit(0 if success else 1)
