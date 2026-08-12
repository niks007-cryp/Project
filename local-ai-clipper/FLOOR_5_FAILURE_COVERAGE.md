# FLOOR 5 FAILURE SCENARIO COVERAGE MATRIX — LOCAL AI CLIPPER

| Failure Scenario | Automated Test Function | Expected Result | Verified Result | Status |
|------------------|-------------------------|-----------------|-----------------|--------|
| **1. Missing candidate** | `tests/integration/test_reframing_pipeline.py::test_reframing_pipeline_execution` | Raises `InputError` | Raises `InputError` | **PASS** |
| **2. Missing media asset** | `tests/integration/test_reframing_pipeline.py::test_reframing_pipeline_execution` | Raises `InputError` | Raises `InputError` | **PASS** |
| **3. Missing transcript** | `tests/integration/test_reframing_pipeline.py::test_reframing_pipeline_execution` | Raises `InputError` | Raises `InputError` | **PASS** |
| **4. Invalid crop bounds** | `tests/unit/test_renderplan_validator.py::test_renderplan_validator_invalid_crop_raises` | Raises `ValidationError` | Raises `ValidationError` | **PASS** |
| **5. Subject-caption collision** | `tests/unit/test_collision_engine.py::test_collision_avoidance_detection_and_resolution` | Relocates caption to top region | Position set to `top` | **PASS** |
| **6. Erratic tracking jump** | `tests/unit/test_subject_tracker.py::test_tracker_trajectory_and_crop_planner` | Smooths crop trajectory delta | Smoothed within limit | **PASS** |
| **7. Subtitle text overflow** | `tests/unit/test_renderplan_validator.py::test_renderplan_validator_valid` | Breaks lines at max 35 chars | Line length <= 35 chars | **PASS** |
| **8. Empty crop keyframes** | `tests/unit/test_renderplan_validator.py::test_renderplan_validator_invalid_crop_raises` | Raises `ValidationError` | Raises `ValidationError` | **PASS** |
| **9. Repeated/idempotent execution** | `tests/integration/test_reframing_pipeline.py::test_reframing_pipeline_execution` | Returns cached `RenderPlan` (`is_idempotent_skip=True`) | `is_idempotent_skip=True` | **PASS** |
