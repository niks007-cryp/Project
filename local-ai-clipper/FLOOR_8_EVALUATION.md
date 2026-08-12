# FLOOR 8 EVALUATION SPECIFICATION — END-TO-END PIPELINE

## Evaluation Metrics

1. **End-to-End Success Rate:** Percentage of valid media inputs converted into rendered clips (Target 100% on valid fixtures).
2. **Candidate Pass Rate:** Ratio of valid rendered assets passing QC (`M <= N`).
3. **Checkpoint Resumability:** 100% successful resumption from last valid checkpoint upon process interruption.
4. **Candidate Failure Isolation:** 0% cascading failures when an individual candidate fails QC or rendering.
5. **Database Independence:** 100% filesystem-based atomic manifest operations without external database dependency.
