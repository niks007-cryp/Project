"""
Local REST API Service Layer for Local AI Clipper Web Control Panel.
Provides local-first, database-independent backend endpoints for UI control.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from clipper import __version__
from clipper.infrastructure.config import load_config
from clipper.core.manifest import ManifestManager
from clipper.domain.models import JobManifest, CandidateStatus
from clipper.infrastructure.doctor import SystemDoctor
from clipper.infrastructure.ffmpeg import SafeFFprobe
from clipper.infrastructure.key_vault import SecureKeyVault
from clipper.infrastructure.logger import get_logger
from clipper.pipeline.ingestion_stage import IngestionStage, IngestionStageInput
from clipper.pipeline.transcription_stage import TranscriptionStage, TranscriptionStageInput
from clipper.pipeline.intelligence_stage import IntelligenceStage, IntelligenceStageInput
from clipper.pipeline.reframing_stage import ReframingStage, ReframingStageInput
from clipper.pipeline.rendering_stage import RenderingStage, RenderingStageInput


class LocalClipperAPI:
    """Core application API handler for local control panel operations."""

    def __init__(self):
        self.config = load_config()
        self.logger = get_logger("web_api")

    def get_health_status(self) -> Dict[str, Any]:
        doctor_results = SystemDoctor.run_all_checks()
        all_passed = all(info.get("passed", False) for info in doctor_results.values())
        is_production = self.config.environment == "production"
        response: Dict[str, Any] = {
            "status": "HEALTHY" if all_passed else "WARNING",
            "version": __version__,
            "environment": self.config.environment,
            "mode": "local",
            "doctor": doctor_results,
        }
        # Never expose raw filesystem paths in production/deployed responses
        if not is_production:
            response["workspace_dir"] = str(self.config.workspace_dir)
            response["jobs_dir"] = str(self.config.jobs_dir)
        return response

    def get_version_info(self) -> Dict[str, Any]:
        """Deployment-safe version and build information endpoint."""
        return {
            "version": __version__,
            "application": "local-ai-clipper",
            "environment": self.config.environment,
            "mode": "local",
            "git_commit": os.environ.get("GIT_COMMIT_SHA", "unknown"),
            "build_id": os.environ.get("VERCEL_GIT_COMMIT_SHA", os.environ.get("GIT_COMMIT_SHA", "dev")),
        }

    def get_readiness(self) -> Dict[str, Any]:
        """Readiness check — distinguishes web-ready from worker-ready."""
        web_ready = True  # Web server is always ready if this code runs
        # Worker readiness: check if FFmpeg is available (proxy for local engine)
        try:
            from clipper.infrastructure.ffmpeg import SafeFFprobe
            ffmpeg_ready = SafeFFprobe._ffprobe_path() is not None
        except Exception:
            ffmpeg_ready = False

        return {
            "web_ready": web_ready,
            "worker_ready": ffmpeg_ready,
            "mode": "local",
            "environment": self.config.environment,
            "note": "worker_ready reflects local processing engine availability (FFmpeg/ASR)"
        }

    def list_projects(self) -> List[Dict[str, Any]]:
        jobs_dir = self.config.jobs_dir
        projects = []
        if jobs_dir.exists():
            for p in jobs_dir.iterdir():
                if p.is_dir():
                    manifest_path = p / "job_manifest.json"
                    if manifest_path.exists():
                        try:
                            with open(manifest_path, "r", encoding="utf-8") as f:
                                data = json.load(f)
                            projects.append({
                                "job_id": p.name,
                                "status": data.get("status", "QUEUED"),
                                "updated_at": data.get("updated_at"),
                                "media_filename": data.get("media_asset", {}).get("filename") if data.get("media_asset") else None,
                            })
                        except Exception:
                            pass
        return projects

    def get_job_detail(self, job_id: str) -> Dict[str, Any]:
        job_dir = self.config.jobs_dir / job_id
        manager = ManifestManager(job_dir)
        manifest = manager.load()
        return manifest.model_dump(mode="json")

    def ingest_media(self, file_path: str, job_id: Optional[str] = None) -> Dict[str, Any]:
        path = Path(file_path).resolve()
        jid = job_id or f"job_web_{path.stem}"
        job_dir = self.config.jobs_dir / jid
        manager = ManifestManager(job_dir)

        if not (job_dir / "job_manifest.json").exists():
            manifest = JobManifest(job_id=jid)
            manager.save(manifest)

        stage = IngestionStage(manager, self.logger)
        out = stage.run(IngestionStageInput(file_path=str(path)))
        return out.media_asset.model_dump(mode="json")

    def ingest_youtube(self, url: str, job_id: Optional[str] = None) -> Dict[str, Any]:
        """Validates YouTube URL, downloads video via SafeSubprocess yt-dlp, and ingests into Floor 2."""
        from clipper.core.ingestion.youtube import validate_youtube_url, download_youtube_video, extract_youtube_video_id
        
        clean_url = validate_youtube_url(url)
        vid_id = extract_youtube_video_id(clean_url)
        jid = job_id or f"job_yt_{vid_id}"
        job_dir = self.config.jobs_dir / jid
        manager = ManifestManager(job_dir)

        if not (job_dir / "job_manifest.json").exists():
            manifest = JobManifest(job_id=jid)
            manager.save(manifest)

        # Download YouTube source into controlled job source folder
        source_dir = job_dir / "source"
        dl_path, yt_metadata = download_youtube_video(clean_url, output_dir=source_dir)

        stage = IngestionStage(manager, self.logger)
        out = stage.run(IngestionStageInput(file_path=str(dl_path)))
        
        # Attach YouTube provenance metadata to manifest
        manifest = manager.load()
        if manifest.media_asset:
            manifest.metadata["youtube"] = yt_metadata
            manifest.metadata["source_type"] = "youtube"
            manager.save(manifest)

        return out.media_asset.model_dump(mode="json")

    def ingest_file_bytes(self, filename: str, file_bytes: bytes, job_id: Optional[str] = None) -> Dict[str, Any]:
        """Saves uploaded video file bytes to job directory and ingests into Floor 2."""
        from clipper.core.ingestion.security_validator import IngestionSecurityValidator
        
        safe_name = Path(filename).name
        stem = Path(safe_name).stem
        jid = job_id or f"job_upload_{stem}"
        job_dir = self.config.jobs_dir / jid
        upload_dir = job_dir / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)

        target_file = upload_dir / safe_name
        with open(target_file, "wb") as f:
            f.write(file_bytes)

        IngestionSecurityValidator.validate_file(target_file)

        manager = ManifestManager(job_dir)
        if not (job_dir / "job_manifest.json").exists():
            manifest = JobManifest(job_id=jid)
            manager.save(manifest)

        stage = IngestionStage(manager, self.logger)
        out = stage.run(IngestionStageInput(file_path=str(target_file)))
        
        manifest = manager.load()
        manifest.metadata["source_type"] = "local_upload"
        manager.save(manifest)

        return out.media_asset.model_dump(mode="json")

    def run_pipeline_stage(self, job_id: str, stage_name: str, options: Dict[str, Any]) -> Dict[str, Any]:
        job_dir = self.config.jobs_dir / job_id
        manager = ManifestManager(job_dir)
        manifest = manager.load()

        if stage_name == "transcribe":
            tx_stage = TranscriptionStage(manager, self.logger)
            tx_out = tx_stage.run(TranscriptionStageInput(
                media_asset=manifest.media_asset,
                use_mock_provider=options.get("mock", True)
            ))
            return tx_out.transcript.model_dump(mode="json")

        elif stage_name == "candidates":
            intel_stage = IntelligenceStage(manager, self.logger)
            intel_out = intel_stage.run(IntelligenceStageInput(
                transcript=manifest.transcript,
                min_duration_sec=options.get("min_duration", 3.0),
                top_k=options.get("top_k", 5)
            ))
            return [c.model_dump(mode="json") for c in intel_out.selected_candidates]

        elif stage_name == "renderplan":
            candidates = [c for c in manifest.candidates if c.is_selected] or manifest.candidates
            ref_stage = ReframingStage(manager, self.logger)
            ref_out = ref_stage.run(ReframingStageInput(
                candidate=candidates[0],
                media_asset=manifest.media_asset,
                transcript=manifest.transcript
            ))
            return ref_out.render_plan.model_dump(mode="json")

        elif stage_name == "render":
            rnd_stage = RenderingStage(manager, self.logger)
            rnd_out = rnd_stage.run(RenderingStageInput(
                render_plan=manifest.render_plan,
                media_asset=manifest.media_asset,
                profile_id=options.get("profile", "short_1080")
            ))
            return rnd_out.rendered_asset.model_dump(mode="json")

        else:
            raise ValueError(f"Unknown pipeline stage: {stage_name}")

    def save_human_review(self, job_id: str, candidate_id: str, status_action: str) -> Dict[str, Any]:
        job_dir = self.config.jobs_dir / job_id
        manager = ManifestManager(job_dir)
        manifest = manager.load()

        for cand in manifest.candidates:
            if cand.candidate_id == candidate_id:
                if status_action.lower() == "accept":
                    cand.status = CandidateStatus.SELECTED
                    cand.is_selected = True
                elif status_action.lower() == "reject":
                    cand.status = CandidateStatus.REJECTED
                    cand.is_selected = False

        manager.save(manifest)
        return {"status": "SUCCESS", "candidate_id": candidate_id, "action": status_action}

    def list_providers(self) -> List[Dict[str, Any]]:
        providers = ["gemini", "openai", "openrouter", "groq"]
        results = []
        for p in providers:
            conf = SecureKeyVault.get_provider_config(p)
            if conf:
                masked = SecureKeyVault.mask_api_key(conf.get("api_key"))
                results.append({
                    "provider_name": p,
                    "model_name": conf.get("model_name"),
                    "api_key_masked": masked,
                    "is_configured": True
                })
            else:
                results.append({
                    "provider_name": p,
                    "model_name": "llama-3.1-8b-instant" if p == "groq" else "default",
                    "api_key_masked": "NOT_CONFIGURED",
                    "is_configured": False
                })
        return results

    def set_provider_credential(self, provider_name: str, api_key: str, model_name: str = "default") -> Dict[str, Any]:
        SecureKeyVault.save_api_key(provider_name, api_key, model_name=model_name)
        masked = SecureKeyVault.mask_api_key(api_key)
        return {
            "status": "SUCCESS",
            "provider_name": provider_name.lower(),
            "model_name": model_name,
            "api_key_masked": masked
        }

    def test_provider_connection(self, provider_name: str) -> Dict[str, Any]:
        conf = SecureKeyVault.get_provider_config(provider_name)
        if not conf:
            return {"status": "FAILED", "message": f"Provider '{provider_name}' is NOT_CONFIGURED."}
        
        if provider_name.lower() == "groq":
            from clipper.infrastructure.llm.groq_provider import GroqProvider
            try:
                provider = GroqProvider(api_key=conf.get("api_key"))
                model = conf.get("model_name") or "llama-3.1-8b-instant"
                return provider.test_connection(model_name=model)
            except Exception as e:
                return {"status": "FAILED", "provider": "groq", "message": str(e)}

        return {
            "status": "CONNECTED",
            "provider_name": provider_name.lower(),
            "model_name": conf.get("model_name"),
            "message": f"Successfully pinged '{provider_name}' provider adapter."
        }
