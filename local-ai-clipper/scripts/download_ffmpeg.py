import urllib.request
import zipfile
import io
import shutil
from pathlib import Path

bin_dir = Path("N:/local-ai-clipper/.bin")
bin_dir.mkdir(parents=True, exist_ok=True)
url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
print("Downloading static FFmpeg bundle from GitHub...")
req = urllib.request.urlopen(url)
zip_data = req.read()
print(f"Downloaded {len(zip_data)} bytes. Extracting...")

with zipfile.ZipFile(io.BytesIO(zip_data)) as z:
    for name in z.namelist():
        if name.endswith("ffmpeg.exe"):
            with z.open(name) as src, open(bin_dir / "ffmpeg.exe", "wb") as dst:
                shutil.copyfileobj(src, dst)
            print("Extracted ffmpeg.exe")
        elif name.endswith("ffprobe.exe"):
            with z.open(name) as src, open(bin_dir / "ffprobe.exe", "wb") as dst:
                shutil.copyfileobj(src, dst)
            print("Extracted ffprobe.exe")

print("Binaries in .bin:", [p.name for p in bin_dir.glob("*.exe")])
