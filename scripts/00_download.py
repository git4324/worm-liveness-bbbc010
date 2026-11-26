"""Download BBBC010 files into data/. Run on your own computer.
Check the file names against https://bbbc.broadinstitute.org/BBBC010 if a URL 404s."""
import pathlib, sys, zipfile, requests

BASE = "https://data.broadinstitute.org/bbbc/BBBC010/"
FILES = [
    "BBBC010_v2_images.zip",
    "BBBC010_v1_foreground.zip",
    "BBBC010_v1_foreground_eachworm.zip",
]
out = pathlib.Path("data"); out.mkdir(exist_ok=True)

for name in FILES:
    dest = out / name
    if not dest.exists():
        print("downloading", name)
        r = requests.get(BASE + name, stream=True, timeout=60)
        if r.status_code != 200:
            sys.exit(f"{name}: HTTP {r.status_code}. Check the exact name on the BBBC010 page.")
        with open(dest, "wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)
    folder = out / dest.stem
    if not folder.exists():
        with zipfile.ZipFile(dest) as z:
            z.extractall(folder)
    print("ready:", folder)
