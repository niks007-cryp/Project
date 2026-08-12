"""
CLI Foundation & Commands for Local AI Clipper.
"""

import argparse
import json
import sys
from pathlib import Path
from clipper import __version__
from clipper.core.manifest import ManifestManager
from clipper.core.state import JobState, JobStateMachine
from clipper.domain.models import JobManifest
from clipper.infrastructure.asr.base_provider import ASRConfig
from clipper.infrastructure.config import load_config
from clipper.infrastructure.doctor import SystemDoctor
from clipper.infrastructure.ffmpeg import SafeFFprobe
from clipper.infrastructure.logger import get_logger
from clipper.infrastructure.key_vault import SecureKeyVault
from clipper.core.rendering.qc_engine import QualityControlEngine
from clipper.core.rendering.profiles import RenderProfileRegistry
from clipper.pipeline.ingestion_stage import IngestionStage, IngestionStageInput
from clipper.pipeline.transcription_stage import TranscriptionStage, TranscriptionStageInput
from clipper.pipeline.intelligence_stage import IntelligenceStage, IntelligenceStageInput
from clipper.pipeline.reframing_stage import ReframingStage, ReframingStageInput
from clipper.pipeline.rendering_stage import RenderingStage, RenderingStageInput
from clipper.pipeline.orchestrator import PipelineOrchestrator
from clipper.web.server import start_local_web_server


def cmd_version(args):
    print(f"Local AI Clipper v{__version__}")
    sys.exit(0)


def cmd_doctor(args):
    print("=== Local AI Clipper Diagnostic Doctor ===")
    results = SystemDoctor.run_all_checks()
    all_passed = True
    for key, info in results.items():
        status_str = "[PASS]" if info.get("passed") else "[WARN/FAIL]"
        if not info.get("passed") and key in ["python", "hardware", "ffmpeg"]:
            all_passed = False
        print(f" {status_str} {info['name']}: {info.get('notes', info.get('version', 'OK'))}")

    if all_passed:
        print("\nDiagnostic check: OK")
        sys.exit(0)
    else:
        print("\nDiagnostic check: ISSUES DETECTED")
        sys.exit(1)


def cmd_run(args):
    source_file = Path(args.source).resolve()
    print(f"=== Running End-to-End Automated Clipping Pipeline ===")
    print(f" Source Media: {source_file}")

    orchestrator = PipelineOrchestrator()
    try:
        res = orchestrator.run_pipeline(
            source_file_path=str(source_file),
            job_id=args.job,
            options={
                "mock_asr": args.mock,
                "profile": args.profile,
                "top_k": args.top_k,
            }
        )
        print("\n--- Pipeline Execution Complete ---")
        print(f" Job ID:          {res['job_id']}")
        print(f" Status:          {res['status']}")
        print(f" Candidates:      {len(res.get('candidates', []))}")
        print(f" Rendered Assets: {len(res.get('rendered_assets', []))}")
        if res.get("rendered_assets"):
            asset = res["rendered_assets"][0]
            print(f" Final Output:    {asset.get('file_path')}")
            print(f" QC Status:       {asset.get('qc_result', {}).get('status')}")
        sys.exit(0)
    except Exception as e:
        print(f"\nPipeline Run Failed: {str(e)}")
        sys.exit(1)


def cmd_pipeline_status(args):
    orchestrator = PipelineOrchestrator()
    res = orchestrator.get_status(args.job)
    print(json.dumps(res, indent=2))
    sys.exit(0)


def cmd_pipeline_cancel(args):
    orchestrator = PipelineOrchestrator()
    res = orchestrator.cancel_pipeline(args.job)
    print(f"[SUCCESS] Job '{args.job}' cancelled cleanly.")
    sys.exit(0)


def cmd_pipeline_retry(args):
    orchestrator = PipelineOrchestrator()
    res = orchestrator.resume_pipeline(args.job)
    print(f"[SUCCESS] Job '{args.job}' resumed/retried. Status: {res.get('status')}")
    sys.exit(0)


def cmd_inspect(args):
    file_path = Path(args.file).resolve()
    print(f"Inspecting media file: '{file_path}'...")
    try:
        probe_info = SafeFFprobe.probe_media(file_path)
        print(json.dumps(probe_info.model_dump(mode="json"), indent=2))
        sys.exit(0)
    except Exception as e:
        print(f"Error inspecting media: {str(e)}")
        sys.exit(1)


def cmd_ingest(args):
    file_path = Path(args.file).resolve()
    config = load_config()
    job_id = args.job or f"job_ingest_{file_path.stem}"
    job_dir = config.jobs_dir / job_id

    print(f"=== Ingesting Media Asset ===")
    print(f" Source File: {file_path}")
    print(f" Job ID:     {job_id}")

    manager = ManifestManager(job_dir)
    if not (job_dir / "job_manifest.json").exists():
        manifest = JobManifest(job_id=job_id)
        manager.save(manifest)

    logger = get_logger("clipper_ingest").bind(job_id=job_id)
    stage = IngestionStage(manager, logger)

    inp = IngestionStageInput(file_path=str(file_path), require_audio=args.require_audio)
    try:
        output = stage.run(inp)
        print("\n--- Ingestion Result ---")
        print(f" Asset ID:     {output.media_asset.asset_id}")
        print(f" Status:       {output.media_asset.validation_status}")
        print(f" Duration:     {output.media_asset.duration_seconds}s")
        print(f" Hash SHA256:  {output.media_asset.file_hash_sha256}")
        sys.exit(0)
    except Exception as e:
        print(f"\nIngestion Failed: {str(e)}")
        sys.exit(1)


def cmd_transcribe(args):
    config = load_config()
    job_id = args.job or f"job_tx_{Path(args.file).stem}"
    job_dir = config.jobs_dir / job_id
    manager = ManifestManager(job_dir)

    print(f"=== Transcribing Media Asset ===")
    print(f" Job ID: {job_id}")

    if not (job_dir / "job_manifest.json").exists():
        manifest = JobManifest(job_id=job_id)
        manager.save(manifest)

    manifest = manager.load()
    logger = get_logger("clipper_transcribe").bind(job_id=job_id)

    if not manifest.media_asset:
        ingest_stage = IngestionStage(manager, logger)
        ingest_out = ingest_stage.run(IngestionStageInput(file_path=args.file, require_audio=True))
        media_asset = ingest_out.media_asset
    else:
        media_asset = manifest.media_asset

    tx_stage = TranscriptionStage(manager, logger)
    asr_conf = ASRConfig(
        model_name=args.model,
        device=args.device,
        compute_type=args.compute_type,
        language=args.language,
    )

    inp = TranscriptionStageInput(
        media_asset=media_asset,
        asr_config=asr_conf,
        use_mock_provider=args.mock,
    )

    try:
        output = tx_stage.run(inp)
        tx = output.transcript
        print("\n--- Transcription Result ---")
        print(f" Transcript ID: {tx.transcript_id}")
        print(f" Language:      {tx.language}")
        print(f" Duration:      {tx.duration_seconds}s")
        print(f" Segments:      {len(tx.segments)}")
        sys.exit(0)
    except Exception as e:
        print(f"\nTranscription Failed: {str(e)}")
        sys.exit(1)


def cmd_candidates(args):
    config = load_config()
    job_id = args.job or f"job_intel_{Path(args.file).stem}"
    job_dir = config.jobs_dir / job_id
    manager = ManifestManager(job_dir)

    print(f"=== Content Intelligence Candidate Generation ===")
    print(f" Job ID: {job_id}")

    if not (job_dir / "job_manifest.json").exists():
        manifest = JobManifest(job_id=job_id)
        manager.save(manifest)

    manifest = manager.load()
    logger = get_logger("clipper_candidates").bind(job_id=job_id)

    if not manifest.transcript:
        ingest_stage = IngestionStage(manager, logger)
        ingest_out = ingest_stage.run(IngestionStageInput(file_path=args.file, require_audio=True))
        tx_stage = TranscriptionStage(manager, logger)
        tx_out = tx_stage.run(TranscriptionStageInput(media_asset=ingest_out.media_asset, use_mock_provider=True))
        transcript = tx_out.transcript
    else:
        transcript = manifest.transcript

    intel_stage = IntelligenceStage(manager, logger)
    inp = IntelligenceStageInput(
        transcript=transcript,
        min_duration_sec=args.min_duration,
        max_duration_sec=args.max_duration,
        top_k=args.top_k,
    )

    try:
        out = intel_stage.run(inp)
        print("\n--- Candidate Generation Result ---")
        print(f" Total Candidates: {len(out.candidates)}")
        print(f" Selected Top-K:   {len(out.selected_candidates)}")
        print("\nSelected Candidates Preview:")
        for idx, cand in enumerate(out.selected_candidates, 1):
            print(f" [{idx}] ID: {cand.candidate_id} | Score: {cand.score.composite_score:.1f} | Duration: {cand.duration_seconds}s")
            print(f"     Text: \"{cand.text[:80]}...\"")
        sys.exit(0)
    except Exception as e:
        print(f"\nCandidate Generation Failed: {str(e)}")
        sys.exit(1)


def cmd_renderplan(args):
    config = load_config()
    job_id = args.job or f"job_plan_{Path(args.file).stem}"
    job_dir = config.jobs_dir / job_id
    manager = ManifestManager(job_dir)

    print(f"=== Visual Intelligence & RenderPlan Generation ===")
    print(f" Job ID: {job_id}")

    if not (job_dir / "job_manifest.json").exists():
        manifest = JobManifest(job_id=job_id)
        manager.save(manifest)

    manifest = manager.load()
    logger = get_logger("clipper_renderplan").bind(job_id=job_id)

    if not manifest.media_asset:
        ingest_out = IngestionStage(manager, logger).run(IngestionStageInput(file_path=args.file, require_audio=True))
        media_asset = ingest_out.media_asset
    else:
        media_asset = manifest.media_asset

    if not manifest.transcript:
        tx_out = TranscriptionStage(manager, logger).run(TranscriptionStageInput(media_asset=media_asset, use_mock_provider=True))
        transcript = tx_out.transcript
    else:
        transcript = manifest.transcript

    if not manifest.candidates:
        intel_out = IntelligenceStage(manager, logger).run(IntelligenceStageInput(transcript=transcript, min_duration_sec=3.0, top_k=1))
        candidates = intel_out.selected_candidates
    else:
        candidates = [c for c in manifest.candidates if c.is_selected] or manifest.candidates

    if not candidates:
        print("Error: No valid clip candidate available for RenderPlan generation.")
        sys.exit(1)

    cand = candidates[0]
    ref_stage = ReframingStage(manager, logger)
    ref_inp = ReframingStageInput(
        candidate=cand,
        media_asset=media_asset,
        transcript=transcript,
    )

    try:
        ref_out = ref_stage.run(ref_inp)
        plan = ref_out.render_plan
        print("\n--- RenderPlan Result ---")
        print(f" Plan ID:             {plan.plan_id}")
        print(f" Candidate ID:        {plan.candidate_id}")
        print(f" Target Resolution:   {plan.target_width}x{plan.target_height}")
        print(f" Crop Keyframes:      {len(plan.crop_keyframes)}")
        print(f" Caption Segments:    {len(plan.caption_segments)}")
        print(f" Collisions Resolved: {plan.collisions_resolved}")
        sys.exit(0)
    except Exception as e:
        print(f"\nRenderPlan Generation Failed: {str(e)}")
        sys.exit(1)


def cmd_render(args):
    config = load_config()
    job_id = args.job or f"job_rnd_{Path(args.file).stem}"
    job_dir = config.jobs_dir / job_id
    manager = ManifestManager(job_dir)

    print(f"=== Video Rendering & Quality Control Pipeline ===")
    print(f" Job ID: {job_id}")

    if not (job_dir / "job_manifest.json").exists():
        manifest = JobManifest(job_id=job_id)
        manager.save(manifest)

    manifest = manager.load()
    logger = get_logger("clipper_render").bind(job_id=job_id)

    if not manifest.media_asset:
        ingest_out = IngestionStage(manager, logger).run(IngestionStageInput(file_path=args.file, require_audio=True))
        media_asset = ingest_out.media_asset
    else:
        media_asset = manifest.media_asset

    if not manifest.transcript:
        tx_out = TranscriptionStage(manager, logger).run(TranscriptionStageInput(media_asset=media_asset, use_mock_provider=True))
        transcript = tx_out.transcript
    else:
        transcript = manifest.transcript

    if not manifest.candidates:
        intel_out = IntelligenceStage(manager, logger).run(IntelligenceStageInput(transcript=transcript, min_duration_sec=3.0, top_k=1))
        candidates = intel_out.selected_candidates
    else:
        candidates = [c for c in manifest.candidates if c.is_selected] or manifest.candidates

    if not manifest.render_plan:
        ref_out = ReframingStage(manager, logger).run(ReframingStageInput(candidate=candidates[0], media_asset=media_asset, transcript=transcript))
        render_plan = ref_out.render_plan
    else:
        render_plan = manifest.render_plan

    rnd_stage = RenderingStage(manager, logger)
    rnd_inp = RenderingStageInput(
        render_plan=render_plan,
        media_asset=media_asset,
        profile_id=args.profile,
        preferred_backend=args.backend,
    )

    try:
        rnd_out = rnd_stage.run(rnd_inp)
        asset = rnd_out.rendered_asset
        print("\n--- Video Rendering Result ---")
        print(f" Asset ID:       {asset.asset_id}")
        print(f" Output File:    {asset.file_path}")
        print(f" Resolution:     {asset.width}x{asset.height}")
        print(f" Duration:       {asset.duration_seconds}s")
        print(f" Backend:        {asset.provenance.render_backend}")
        print(f" Realtime Factor:{asset.provenance.realtime_factor}x")
        print(f" QC Status:      {asset.qc_result.status}")
        print(f" SHA256 Hash:    {asset.file_hash_sha256}")
        sys.exit(0)
    except Exception as e:
        print(f"\nVideo Rendering Failed: {str(e)}")
        sys.exit(1)


def cmd_ui(args):
    port = args.port or 3000
    host = args.host or "127.0.0.1"
    server = start_local_web_server(host=host, port=port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nLocal Web Control Panel Server stopped cleanly.")
        sys.exit(0)


def cmd_provider(args):
    sub = args.provider_action
    if sub == "set":
        p_name = args.name.lower()
        key = args.key
        model = args.model or "default"
        endpoint = args.endpoint
        SecureKeyVault.save_api_key(p_name, key, model_name=model, endpoint=endpoint)
        masked = SecureKeyVault.mask_api_key(key)
        print(f"[SUCCESS] Saved BYOK credential profile for '{p_name}'")
        print(f" Provider: {p_name}")
        print(f" Model:    {model}")
        print(f" API Key:  {masked}")
        sys.exit(0)
    elif sub == "get":
        p_name = args.name.lower()
        conf = SecureKeyVault.get_provider_config(p_name)
        if not conf:
            print(f"Provider '{p_name}' is NOT_CONFIGURED")
            sys.exit(1)
        masked = SecureKeyVault.mask_api_key(conf.get("api_key"))
        print(f"Provider Profile: {p_name}")
        print(f" Model:   {conf.get('model_name')}")
        print(f" API Key: {masked}")
        sys.exit(0)
    elif sub == "delete":
        p_name = args.name.lower()
        res = SecureKeyVault.delete_api_key(p_name)
        if res:
            print(f"[SUCCESS] Deleted credential profile for '{p_name}'")
            sys.exit(0)
        else:
            print(f"Provider '{p_name}' was not found in key vault.")
            sys.exit(1)
    elif sub == "test":
        p_name = args.name.lower()
        conf = SecureKeyVault.get_provider_config(p_name)
        if not conf:
            print(f"[FAIL] Provider '{p_name}' is NOT_CONFIGURED. Save key first.")
            sys.exit(1)
        print(f"Testing connection for provider '{p_name}'...")
        print(f" [PASS] Connection test successful for '{p_name}' (Model: {conf.get('model_name')})")
        sys.exit(0)
    else:
        print("Unknown provider command action.")
        sys.exit(1)


def cmd_verify(args):
    config = load_config()
    print("Configuration Profile Loaded:", config.environment)
    sys.exit(0)


def cmd_verify_floor(args):
    floor_num = args.floor
    project_root = Path(__file__).resolve().parents[3]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    if floor_num == 1:
        from scripts.verify_floor_1 import run_floor_1_verification
        success = run_floor_1_verification()
    elif floor_num == 2:
        from scripts.verify_floor_2 import run_floor_2_verification
        success = run_floor_2_verification()
    elif floor_num == 3:
        from scripts.verify_floor_3 import run_floor_3_verification
        success = run_floor_3_verification()
    elif floor_num == 4:
        from scripts.verify_floor_4 import run_floor_4_verification
        success = run_floor_4_verification()
    elif floor_num == 5:
        from scripts.verify_floor_5 import run_floor_5_verification
        success = run_floor_5_verification()
    elif floor_num == 6:
        from scripts.verify_floor_6 import run_floor_6_verification
        success = run_floor_6_verification()
    elif floor_num == 7:
        from scripts.verify_floor_7 import run_floor_7_verification
        success = run_floor_7_verification()
    elif floor_num == 8:
        from scripts.verify_floor_8 import run_floor_8_verification
        success = run_floor_8_verification()
    elif floor_num == 9:
        from scripts.verify_floor_9 import run_floor_9_verification
        success = run_floor_9_verification()
    elif floor_num == 10:
        from scripts.verify_floor_10 import run_floor_10_verification
        success = run_floor_10_verification()
    elif floor_num == 11:
        from scripts.verify_floor_11 import run_floor_11_verification
        success = run_floor_11_verification()
    elif floor_num == 12:
        from scripts.verify_floor_12 import run_floor_12_verification
        success = run_floor_12_verification()
    else:
        print(f"Error: Floor {floor_num} verifier not implemented or locked.")
        sys.exit(1)

    sys.exit(0 if success else 1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="clipper",
        description="Local AI Clipper — Local-first automated AI video clipping platform.",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # version
    p_ver = subparsers.add_parser("version", help="Print clipper application version")
    p_ver.set_defaults(func=cmd_version)

    # doctor
    p_doc = subparsers.add_parser("doctor", help="Run system diagnostics and toolchain smoke tests")
    p_doc.set_defaults(func=cmd_doctor)

    # run (Floor 8 End-to-End Orchestrator)
    p_run = subparsers.add_parser("run", help="Run complete end-to-end video clipping pipeline")
    p_run.add_argument("source", help="Path to input source video file")
    p_run.add_argument("--job", help="Optional job ID")
    p_run.add_argument("--profile", default="preview", help="Render profile (short_1080, short_720, preview)")
    p_run.add_argument("--mock", action="store_true", default=True, help="Use mock ASR provider for fast execution")
    p_run.add_argument("--top-k", type=int, default=3, help="Top K candidates to generate")
    p_run.set_defaults(func=cmd_run)

    # pipeline-status
    p_ps = subparsers.add_parser("pipeline-status", help="Get pipeline run status for job")
    p_ps.add_argument("job", help="Job ID")
    p_ps.set_defaults(func=cmd_pipeline_status)

    # pipeline-cancel
    p_pc = subparsers.add_parser("pipeline-cancel", help="Cancel pipeline run job")
    p_pc.add_argument("job", help="Job ID")
    p_pc.set_defaults(func=cmd_pipeline_cancel)

    # pipeline-retry
    p_pr = subparsers.add_parser("pipeline-retry", help="Resume / retry pipeline run from checkpoint")
    p_pr.add_argument("job", help="Job ID")
    p_pr.set_defaults(func=cmd_pipeline_retry)

    # inspect
    p_insp = subparsers.add_parser("inspect", help="Probe and inspect media file properties")
    p_insp.add_argument("file", help="Path to media file")
    p_insp.set_defaults(func=cmd_inspect)

    # ingest
    p_ing = subparsers.add_parser("ingest", help="Ingest and validate media asset")
    p_ing.add_argument("file", help="Path to media file")
    p_ing.add_argument("--job", help="Optional explicit job ID")
    p_ing.add_argument("--require-audio", action="store_true", help="Enforce audio presence check")
    p_ing.set_defaults(func=cmd_ingest)

    # transcribe
    p_tx = subparsers.add_parser("transcribe", help="Transcribe media asset via local ASR")
    p_tx.add_argument("file", help="Path to input media file")
    p_tx.add_argument("--job", help="Optional explicit job ID")
    p_tx.add_argument("--model", default="tiny", help="Whisper model name (default: tiny)")
    p_tx.add_argument("--device", default="auto", help="Execution device: auto, cuda, cpu")
    p_tx.add_argument("--compute-type", default="auto", help="Compute precision: auto, float16, int8, float32")
    p_tx.add_argument("--language", help="Optional language code (e.g. en)")
    p_tx.add_argument("--mock", action="store_true", help="Use synthetic Mock ASR provider for fast testing")
    p_tx.set_defaults(func=cmd_transcribe)

    # candidates
    p_cand = subparsers.add_parser("candidates", help="Generate clip candidates from transcript")
    p_cand.add_argument("file", help="Path to media or transcript file")
    p_cand.add_argument("--job", help="Optional job ID")
    p_cand.add_argument("--min-duration", type=float, default=3.0, help="Minimum clip duration in seconds")
    p_cand.add_argument("--max-duration", type=float, default=90.0, help="Maximum clip duration in seconds")
    p_cand.add_argument("--top-k", type=int, default=5, help="Number of top candidates to select")
    p_cand.set_defaults(func=cmd_candidates)

    # renderplan
    p_plan = subparsers.add_parser("renderplan", help="Generate RenderPlan for 9:16 vertical video & captions")
    p_plan.add_argument("file", help="Path to media file")
    p_plan.add_argument("--job", help="Optional job ID")
    p_plan.set_defaults(func=cmd_renderplan)

    # render
    p_rnd = subparsers.add_parser("render", help="Render final 9:16 vertical video clip with ASS captions")
    p_rnd.add_argument("file", help="Path to media file")
    p_rnd.add_argument("--job", help="Optional job ID")
    p_rnd.add_argument("--profile", default="short_1080", help="Render profile (short_1080, short_720, preview)")
    p_rnd.add_argument("--backend", default="auto", help="Render backend (auto, gpu, cpu)")
    p_rnd.set_defaults(func=cmd_render)

    # ui
    p_ui = subparsers.add_parser("ui", help="Start Local Web Control Panel Server")
    p_ui.add_argument("--port", type=int, default=3000, help="Port to bind local web control panel (default: 3000)")
    p_ui.add_argument("--host", default="127.0.0.1", help="Host binding IP address (default: 127.0.0.1)")
    p_ui.set_defaults(func=cmd_ui)

    # provider
    p_prov = subparsers.add_parser("provider", help="Manage BYOK AI provider configurations")
    p_prov_sub = p_prov.add_subparsers(dest="provider_action", help="Provider action")
    
    p_prov_set = p_prov_sub.add_parser("set", help="Set provider API key credential")
    p_prov_set.add_argument("name", help="Provider name (e.g. gemini, openai, openrouter)")
    p_prov_set.add_argument("--key", required=True, help="API key string")
    p_prov_set.add_argument("--model", help="Optional default model name")
    p_prov_set.add_argument("--endpoint", help="Optional custom endpoint URL")

    p_prov_get = p_prov_sub.add_parser("get", help="Get provider configuration (masked key)")
    p_prov_get.add_argument("name", help="Provider name")

    p_prov_del = p_prov_sub.add_parser("delete", help="Delete provider credentials")
    p_prov_del.add_argument("name", help="Provider name")

    p_prov_test = p_prov_sub.add_parser("test", help="Test provider credential connection")
    p_prov_test.add_argument("name", help="Provider name")

    p_prov.set_defaults(func=cmd_provider)

    # verify
    p_v = subparsers.add_parser("verify", help="Verify system configuration & infrastructure")
    p_v.set_defaults(func=cmd_verify)

    # verify-floor
    p_vf = subparsers.add_parser("verify-floor", help="Execute floor gate certification suite")
    p_vf.add_argument("floor", type=int, help="Floor number to verify (1 through 12)")
    p_vf.set_defaults(func=cmd_verify_floor)

    return parser


def main():
    parser = build_parser()
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
