"""
Content Intelligence Pipeline Stage for Local AI Clipper.
"""

import hashlib
import json
import time
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field
from clipper.core.manifest import ManifestManager
from clipper.core.errors import ValidationError, InputError
from clipper.core.intelligence.candidate_generator import CandidateGenerator
from clipper.core.intelligence.validator import CandidateValidator
from clipper.core.intelligence.feature_extractor import FeatureExtractor
from clipper.core.intelligence.scoring_engine import ScoringEngine, ScoringWeights
from clipper.core.intelligence.deduplicator import CandidateDeduplicator
from clipper.core.intelligence.ranker import CandidateRanker
from clipper.domain.models import Transcript, ClipCandidate
from clipper.infrastructure.llm.base_provider import LLMConfig, LLMProvider
from clipper.infrastructure.llm.mock_provider import MockLLMProvider
from clipper.infrastructure.logger import ContextLogger
from clipper.pipeline.stage import BaseStage


class IntelligenceStageInput(BaseModel):
    transcript: Transcript
    min_duration_sec: float = 15.0
    max_duration_sec: float = 90.0
    top_k: int = 5
    scoring_weights: ScoringWeights = Field(default_factory=ScoringWeights)
    use_llm_scoring: bool = False
    llm_config: LLMConfig = Field(default_factory=LLMConfig)


class IntelligenceStageOutput(BaseModel):
    candidates: List[ClipCandidate]
    selected_candidates: List[ClipCandidate]
    is_idempotent_skip: bool = False


class IntelligenceStage(BaseStage[IntelligenceStageInput, IntelligenceStageOutput]):
    """
    Production-grade Content Intelligence Pipeline Stage.
    Flow:
    TRANSCRIPT -> BOUNDARY DETECTION -> CANDIDATE GENERATION -> CANDIDATE VALIDATION -> FEATURE EXTRACTION -> SCORING -> DEDUPLICATION -> RANKING -> CHECKPOINT
    """

    stage_name = "intelligence"

    def validate_input(self, input_data: IntelligenceStageInput) -> None:
        if not input_data.transcript or not input_data.transcript.segments:
            raise InputError("Input transcript is empty or missing segments.")

    def execute_logic(self, input_data: IntelligenceStageInput) -> IntelligenceStageOutput:
        tx = input_data.transcript
        manifest = self.manifest_manager.load()
        job_dir = self.manifest_manager.job_dir

        # Hash for idempotency check
        config_payload = json.dumps(
            {
                "weights": input_data.scoring_weights.model_dump(),
                "min_dur": input_data.min_duration_sec,
                "max_dur": input_data.max_duration_sec,
                "top_k": input_data.top_k,
            },
            sort_keys=True,
        )
        config_hash = hashlib.sha256(config_payload.encode("utf-8")).hexdigest()[:12]

        # Check manifest idempotency
        if manifest.candidates and len(manifest.candidates) > 0 and manifest.metadata.get("intelligence_config_hash") == config_hash:
            self.logger.info(f"Idempotent intelligence skip: Candidates for transcript {tx.transcript_id} already generated.")
            selected = [c for c in manifest.candidates if c.is_selected]
            return IntelligenceStageOutput(
                candidates=manifest.candidates,
                selected_candidates=selected,
                is_idempotent_skip=True,
            )

        # 1. Candidate Generation
        proposed_cands = CandidateGenerator.generate_candidates(
            tx,
            min_duration_sec=input_data.min_duration_sec,
            max_duration_sec=input_data.max_duration_sec,
        )

        if not proposed_cands:
            self.logger.warning(f"No candidate clip windows could be generated for transcript {tx.transcript_id}.")
            return IntelligenceStageOutput(candidates=[], selected_candidates=[], is_idempotent_skip=False)

        # 2. Candidate Validation, Feature Extraction & Scoring
        llm_provider: Optional[LLMProvider] = MockLLMProvider() if input_data.use_llm_scoring else None
        valid_cands: List[ClipCandidate] = []

        for cand in proposed_cands:
            try:
                CandidateValidator.validate_candidate(
                    cand,
                    transcript=tx,
                    min_duration_sec=input_data.min_duration_sec,
                    max_duration_sec=input_data.max_duration_sec,
                )
                cand.feature_vector = FeatureExtractor.extract_features(cand)

                # Calculate composite score
                cand.score = ScoringEngine.calculate_score(cand, weights=input_data.scoring_weights)
                valid_cands.append(cand)
            except ValidationError as e:
                self.logger.debug(f"Candidate {cand.candidate_id} rejected during validation: {str(e)}")

        # 3. Deduplication & Overlap Resolution
        deduped_cands = CandidateDeduplicator.deduplicate_candidates(valid_cands)

        # 4. Ranking & Selection
        final_ranked = CandidateRanker.rank_candidates(deduped_cands, top_k=input_data.top_k)
        selected_cands = [c for c in final_ranked if c.is_selected]

        # Save artifacts to job directory
        intel_dir = job_dir / "intelligence"
        intel_dir.mkdir(parents=True, exist_ok=True)
        cand_file = intel_dir / "candidates.json"

        with open(cand_file, "w", encoding="utf-8") as f:
            json.dump([c.model_dump(mode="json") for c in final_ranked], f, indent=2, default=str)

        manifest.candidates = final_ranked
        manifest.metadata["intelligence_config_hash"] = config_hash
        self.manifest_manager.save(manifest)

        return IntelligenceStageOutput(
            candidates=final_ranked,
            selected_candidates=selected_cands,
            is_idempotent_skip=False,
        )

    def validate_output(self, output_data: IntelligenceStageOutput) -> None:
        for c in output_data.selected_candidates:
            if not c.is_selected:
                raise ValueError(f"Candidate {c.candidate_id} in selected list is not marked is_selected=True.")
