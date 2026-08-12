# FLOOR 12 — INCIDENT RESPONSE & FAILURE TAXONOMY TESTS

## Simulated Incident Scenarios

| Incident Scenario | Classification | Expected Handling | Verified Behavior | Status |
|-------------------|----------------|-------------------|-------------------|--------|
| **Non-existent Source File** | `InputError` | Halt at ingestion, record error in stage status | Stage status `FAILED` with clear note | PASS |
| **Missing Audio Stream** | `InputError` | Flag audio requirement failure | Ingestion validation rejects asset | PASS |
| **Invalid Crop Coordinates** | `ValidationError` | Reframing stage boundary rejection | Plan validator raises exception | PASS |
| **Unconfigured AI Provider**| `ExternalProviderNotConfiguredError` | Halt cleanly, notify user to configure key | Prompt user to configure key | PASS |
| **Interrupted Execution** | Job Checkpointing | Resume pipeline from last successful stage | Skipped completed stages | PASS |
