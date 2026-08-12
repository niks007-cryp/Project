from clipper.core.state import JobState
from clipper.domain.models import JobManifest
m = JobManifest(job_id="test")
m.status = JobState.SUCCEEDED
d = m.model_dump(mode="json")
print("status value:", repr(d["status"]))
print("enum value:", repr(JobState.SUCCEEDED.value))
print("match:", d["status"] == JobState.SUCCEEDED.value)
