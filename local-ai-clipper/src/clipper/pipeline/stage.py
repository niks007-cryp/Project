"""
Generic Pipeline Stage Abstraction & Contract for Local AI Clipper.
"""

import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Generic, TypeVar, Any, Dict
from pydantic import BaseModel
from clipper.core.errors import ValidationError, ClipperError
from clipper.core.manifest import ManifestManager
from clipper.domain.models import StageStatus
from clipper.infrastructure.logger import ContextLogger

InputT = TypeVar("InputT", bound=BaseModel)
OutputT = TypeVar("OutputT", bound=BaseModel)


class BaseStage(ABC, Generic[InputT, OutputT]):
    """
    Abstract Base Class for all pipeline stages.
    Enforces the stage execution lifecycle contract:
    validate_input -> execute -> validate_output -> checkpoint -> emit_result
    """

    stage_name: str = "base_stage"

    def __init__(self, manifest_manager: ManifestManager, logger: ContextLogger):
        self.manifest_manager = manifest_manager
        self.logger = logger.bind(stage=self.stage_name)

    @abstractmethod
    def validate_input(self, input_data: InputT) -> None:
        """Validates input payload prior to execution."""
        pass

    @abstractmethod
    def execute_logic(self, input_data: InputT) -> OutputT:
        """Core execution logic implemented by subclass."""
        pass

    @abstractmethod
    def validate_output(self, output_data: OutputT) -> None:
        """Validates output payload following execution."""
        pass

    def run(self, input_data: InputT) -> OutputT:
        """
        Orchestrates full stage lifecycle contract.
        """
        start_time = datetime.utcnow()
        t0 = time.time()
        self.logger.info(f"Starting stage execution: {self.stage_name}")

        manifest = self.manifest_manager.load()
        stage_status = manifest.stages.get(
            self.stage_name,
            StageStatus(stage_name=self.stage_name, status="RUNNING", start_time=start_time),
        )
        stage_status.status = "RUNNING"
        stage_status.start_time = start_time
        manifest.stages[self.stage_name] = stage_status
        self.manifest_manager.save(manifest)

        try:
            # 1. Validate Input
            self.validate_input(input_data)

            # 2. Execute Stage Logic
            output = self.execute_logic(input_data)

            # 3. Validate Output
            self.validate_output(output)

            # 4. Record Success & Checkpoint
            duration_ms = round((time.time() - t0) * 1000, 2)
            end_time = datetime.utcnow()

            manifest = self.manifest_manager.load()
            stage_status = manifest.stages[self.stage_name]
            stage_status.status = "SUCCEEDED"
            stage_status.end_time = end_time
            stage_status.duration_ms = duration_ms
            stage_status.error_message = None
            manifest.stages[self.stage_name] = stage_status
            self.manifest_manager.save(manifest)

            self.logger.info(
                f"Completed stage execution: {self.stage_name}",
                extra={"duration_ms": duration_ms, "status": "SUCCEEDED"},
            )
            return output

        except Exception as e:
            duration_ms = round((time.time() - t0) * 1000, 2)
            end_time = datetime.utcnow()
            error_msg = str(e)

            manifest = self.manifest_manager.load()
            stage_status = manifest.stages[self.stage_name]
            stage_status.status = "FAILED"
            stage_status.end_time = end_time
            stage_status.duration_ms = duration_ms
            stage_status.error_message = error_msg
            manifest.stages[self.stage_name] = stage_status
            self.manifest_manager.save(manifest)

            self.logger.error(
                f"Stage execution failed: {self.stage_name} - {error_msg}",
                extra={"duration_ms": duration_ms, "status": "FAILED", "error_type": type(e).__name__},
            )
            if isinstance(e, ClipperError):
                raise e
            raise ValidationError(f"Stage '{self.stage_name}' failed: {error_msg}")
