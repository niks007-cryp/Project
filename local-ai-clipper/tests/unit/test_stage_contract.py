"""
Unit Tests for BaseStage Generic Pipeline Contract.
"""

import pytest
from pydantic import BaseModel
from clipper.pipeline.stage import BaseStage
from clipper.core.errors import ValidationError


class MockInput(BaseModel):
    value: int


class MockOutput(BaseModel):
    result: int


class SampleDummyStage(BaseStage[MockInput, MockOutput]):
    stage_name = "dummy_stage"

    def validate_input(self, input_data: MockInput) -> None:
        if input_data.value < 0:
            raise ValidationError("Input value cannot be negative")

    def execute_logic(self, input_data: MockInput) -> MockOutput:
        return MockOutput(result=input_data.value * 2)

    def validate_output(self, output_data: MockOutput) -> None:
        if output_data.result > 100:
            raise ValidationError("Output result exceeds limit")


def test_stage_contract_successful_lifecycle(manifest_manager, logger):
    stage = SampleDummyStage(manifest_manager, logger)
    inp = MockInput(value=10)
    
    out = stage.run(inp)
    assert out.result == 20

    # Assert stage status persisted to manifest
    manifest = manifest_manager.load()
    assert "dummy_stage" in manifest.stages
    assert manifest.stages["dummy_stage"].status == "SUCCEEDED"
    assert manifest.stages["dummy_stage"].duration_ms is not None


def test_stage_contract_validation_failure(manifest_manager, logger):
    stage = SampleDummyStage(manifest_manager, logger)
    inp = MockInput(value=-5)  # Triggers input validation failure

    with pytest.raises(ValidationError):
        stage.run(inp)

    # Assert manifest records stage failure
    manifest = manifest_manager.load()
    assert manifest.stages["dummy_stage"].status == "FAILED"
    assert "negative" in manifest.stages["dummy_stage"].error_message
