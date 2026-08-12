import sys, subprocess, tempfile
from pathlib import Path
sys.path.insert(0, str(Path("N:/local-ai-clipper")))
from tests.fixtures.media_generator import SyntheticMediaGenerator

project_root = Path("N:/local-ai-clipper")

with tempfile.TemporaryDirectory() as td:
    mp4_path = SyntheticMediaGenerator.generate_valid_mp4(Path(td) / "speech.mp4", duration_sec=10)
    cli_cmd = [
        sys.executable, "-m", "clipper.cli.main",
        "transcribe", str(mp4_path),
        "--mock", "--model", "whisper-tiny", "--device", "cpu"
    ]
    print("CMD:", cli_cmd)
    res = subprocess.run(cli_cmd, capture_output=True, text=True, cwd=str(project_root))
    print("RETURNCODE:", res.returncode)
    print("STDOUT:", res.stdout[-2000:])
    print("STDERR:", res.stderr[-1000:])
