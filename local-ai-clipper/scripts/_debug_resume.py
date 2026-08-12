import sys, time, tempfile
from pathlib import Path
sys.path.insert(0, str(Path("N:/local-ai-clipper")))
from clipper.pipeline.orchestrator import PipelineOrchestrator
from clipper.core.state import JobState
from tests.fixtures.media_generator import SyntheticMediaGenerator

with tempfile.TemporaryDirectory() as td:
    media_file = Path(td) / "t.mp4"
    SyntheticMediaGenerator.generate_valid_mp4(media_file, duration_sec=10)
    orch = PipelineOrchestrator()
    jid = f"job_debugtest_{time.time_ns()}"
    r1 = orch.run_pipeline(str(media_file), job_id=jid, options={"mock_asr": True})
    print("RUN STATUS:", repr(r1["status"]))
    r2 = orch.resume_pipeline(jid, options={"mock_asr": True})
    print("RESUME STATUS:", repr(r2["status"]))
    print("EXPECTED:", repr(JobState.SUCCEEDED.value))
    print("MATCH:", r2["status"] == JobState.SUCCEEDED.value)
