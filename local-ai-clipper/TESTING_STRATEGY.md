# TESTING STRATEGY — LOCAL AI CLIPPER

## 1. Testing Pyramid

```
                / \
               /   \  E2E Pipeline Integration Tests (10%)
              /-----\
             /       \  Component / Stage Integration Tests (30%)
            /---------\
           /           \  Unit & Schema Validation Tests (60%)
          /-------------\
```

## 2. Test Suites & Verification Levels

### 2.1 Unit Tests (Level 1)
- **Coverage:** Fast deterministic tests (<100ms per test).
- **Scope:**
  - Pydantic schema validation & serialization.
  - Timestamp boundary clamping algorithms.
  - Subtitle ASS string formatting & line wrapping logic.
  - FFmpeg parameter list builder functions.

### 2.2 Integration Tests (Level 2)
- **Coverage:** Synthetic fixture tests using short 5-second sample audio/video files.
- **Scope:**
  - Audio extraction subprocess execution.
  - Mocked ASR response parsing.
  - Mocked LLM candidate JSON response parsing.
  - ASS file creation and rendering pipeline verification.

### 2.3 End-to-End Pipeline Tests (Level 3)
- **Coverage:** Full job execution using representative 30-second test video.
- **Scope:** Complete execution from `clipper process` to `QCReport` generation.

## 3. Floor Gate Verification Command (`clipper verify-floor <N>`)
Floor progression requires passing the explicit floor verifier harness:
- Executes unit & integration tests assigned to that floor.
- Asserts zero failing tests.
- Checks documentation and risk register status.
- Generates a signed local certification manifest unlocking the next floor.
